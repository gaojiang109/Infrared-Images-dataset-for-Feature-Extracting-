﻿# -*- coding: utf-8 -*-
"""
Created on Tue Dec  4 06:24:03 2018

@author: Zongjiang GAO
"""

from keras.models import  load_model
from keras import applications
from keras import backend as K
from scipy.stats import entropy
from keras.preprocessing import image
from keras.applications.vgg19 import preprocess_input
from keras.layers import Dropout, Flatten, Dense, GlobalAveragePooling2D

import numpy as np
import matplotlib.pyplot as plt
from  skimage import color

img_width, img_height =224, 224 
layer_extract=[12,44,81]
 # the output layer 
#num=10    # the number of output at a specifice layer 

def entropy1(labels, base=None):
  value,counts = np.unique(labels, return_counts=True)
  return entropy(counts, base=base)

def avg(input):
  input2 = np.asarray(input, dtype=np.double)  #防止计算过程中溢出，转换为double类型，https://blog.csdn.net/u012005313/article/details/84035371
  #print('avg input----------------------')
  #print( np.shape(input2) )
  
  input3=np.squeeze(input2) #the shape of input is [1,X,X], so the first dimenon should be deleted.
  #print('squeezed ----------------------')
  #print( np.shape(input3) )

  grad=np.gradient(input3)  
  row,col=np.shape(grad[0]) #get the shape of grad
  out1=np.sqrt((np.square(grad[0])+np.square(grad[1]))/2)   
  avg=np.sum(out1)/row/col
  
  return(avg)
  
    
#test image 
#img_path = ''# the result is good.
#img_path = 'Jeep_IR.bmp' # the result is bad.
#img_path = 'Road_IR.jpg' #VIS_18dhvR.bmp #
#img_path = 'AMB6806a.bmp'
#img_path = '4907i.bmp' 
#img_path = 'IR_maninhuis_g.bmp'  
#img_path = 'Octec_IR.jpg'
# c =AIM2518a.bmp h=RAD28.bmp
img_path='1800i.bmp'

img = image.load_img(img_path, target_size=(224, 224))
img = image.img_to_array(img)
img=color.gray2rgb(img)
img = np.expand_dims(img, axis=0)  #add  an axis to the image, because the input should have four aixes.
img_input=img

#img_input = preprocess_input(img)  #VGG19 need to preprocess_input
#print("The the shape of image to be processed is:", img_input.shape)

model = applications.MobileNet(weights = "imagenet", include_top=True, input_shape = (img_width, img_height, 3))
###load the trained model
model_trained = load_model('mobilenet1121.h5')
print(img_path)

model.summary()
print('.........................................')
model_trained.summary()



for i in range(3):
    layer=layer_extract[i]

#model_trained.summary()
    print('---------------------------layer =',layer)
    #print('length of model_trained layer',len(model_trained.layers))
    print('model_trained.layers[layer]',model_trained.layers[layer])    
    
    #model_trained = load_model('vgg19_10.h5')
    ### get how many output at a specifice layer
    get_layer_output = K.function([model.layers[0].input],[model.layers[layer].output])
    output_num =(get_layer_output([img_input])[0]).shape[3]
    ent=np.zeros((output_num,2)) # ent is an array to store the entropy. The first column saves the entropy from vgg19 network. 
                               #The second column saves the entropy from trained vgg19 network
    
    av_grad=np.zeros((output_num,2)) # av_grad is an array to store average gradient. The first column saves the average gradient from vgg19 network. 
                               #The second column saves the average gradient from trained vgg19 network
    
    print('Total number of the layer is ',output_num)
    #print(ent)
    
    #print('The shape of output is', get_layer_output([img_input])[0].shape)
    
    for num in range(0, output_num):
       ### original vgg19 network output at [layer] 
      get_layer_output = K.function([model.layers[0].input],[model.layers[layer].output]) 
      output =(get_layer_output([img_input])[0])[:,:,:,num]
      ent[num,0]=entropy1(output)  
      av_grad[num,0]=avg(output)
      
      
      # the transfer learned network output at [layer]
      get_trained_layer_output = K.function([model_trained.layers[0].input],[model_trained.layers[layer].output])
      trained_output =get_trained_layer_output([img_input])[0][:,:,:,num]
      ent[num,1]=entropy1(trained_output)
      av_grad[num,1]=avg(trained_output) #compute the average gradient of output, and save it in the array.
      
    '''
    print('#########################################')
    print(img_path) #print the name of image
    print('the number of layer is',layer)
    #np.save('entropy',ent)
    #np.save('average_gradient',av_grad)
    result_path='/home/user1/Documents/transfer2/MN_result'
    
    
    plt.plot(ent[:,0],'b')
    plt.ylabel('entropy')
    plt.xlabel('number')
    plt.legend([('original mobilenet')], loc='upper right')
    plt.savefig(result_path+r'//'+str(layer)+'MN_ENT_TRANS.jpg')
    plt.gcf().clear()
    
    plt.plot(ent[:,1],'r')
    plt.ylabel('entropy')
    plt.xlabel('number')
    plt.legend([('transfer learned')], loc='upper right')
    plt.savefig(result_path+r'//'+str(layer)+'MN_ENT_TRANS.jpg')
    
    plt.gcf().clear()
    
    plt.plot(av_grad[:,0],'b')
    plt.ylabel('average gradient')
    plt.xlabel('number')
    plt.legend([('original MN')], loc='upper right')
    plt.savefig(result_path+r'//'+str(layer)+'MN_AVG_ORG.jpg')
    
    plt.gcf().clear()
    
    plt.plot(av_grad[:,1],'r')
    plt.ylabel('average gradient')
    plt.xlabel('number')
    plt.legend([('transfer learned')], loc='upper right')
    plt.savefig(result_path+r'//'+str(layer)+'MN_AVG_TRANS.jpg')
    
    plt.gcf().clear()
    '''
    print('MN original network output entropy is:')
    print(entropy1(output))
    print(output.shape)
    #print(output.astype(int))
    
    print('transfer learned network output entropy is:')
    print(entropy1(trained_output))
    print(trained_output.shape)
    
    #ent=np.load('entropy.npy') # load the entropy matrix
    print('first is original,second is transfer learned. The sum of entropy is:')
    print(np.sum(ent, axis=0))
    
    print('first is original,second is transfer learned. The sum of AG is:')
    print(np.sum(av_grad, axis=0))
    
    print('first is original,second is transfer learned. The entropy variation is:')
    print(np.var(ent,axis=0))
    
    print('#################################################################')
    
    
