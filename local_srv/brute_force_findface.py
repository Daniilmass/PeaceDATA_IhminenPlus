import os
import time
import openface
import cv2
import pickle

import numpy as np

__author__ = 'voldemarich'

openface_model_dir = "/home/voldemarich/myinstall/openface/models"
dlib_model_path = os.path.join(openface_model_dir, "dlib", "shape_predictor_68_face_landmarks.dat")
openface_model_path = os.path.join(openface_model_dir, "openface", "nn4.small2.v1.t7")

std_img_dimension = 96  # aligning faces to imgs of (std_img_dimension x std_img_dimension) size

align = openface.AlignDlib(dlib_model_path)
net = openface.TorchNeuralNet(openface_model_path, std_img_dimension)
verbose = True
print("LOADED LIBS")

def getRep(imgPath):
    start = time.time()
    bgrImg = cv2.imread(imgPath)
    if bgrImg is None:
        raise Exception("Unable to load image: {}".format(imgPath))

    rgbImg = cv2.cvtColor(bgrImg, cv2.COLOR_BGR2RGB)

    if verbose:
        print("  + Original size: {}".format(rgbImg.shape))
    if verbose:
        print("Loading the image took {} seconds.".format(time.time() - start))

    start = time.time()

    bb = align.getLargestFaceBoundingBox(rgbImg)
    if bb is None:
        raise Exception("Unable to find a face: {}".format(imgPath))
    if verbose:
        print("Face detection took {} seconds.".format(time.time() - start))

    start = time.time()
    alignedFace = align.align_v1(std_img_dimension, rgbImg, bb,
                                 landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)
    if alignedFace is None:
        raise Exception("Unable to align image: {}".format(imgPath))
    if verbose:
        print("Alignment took {} seconds.".format(time.time() - start))

    start = time.time()
    rep = net.forward(alignedFace)
    if verbose:
        print("Neural network forward pass took {} seconds.".format(
            time.time() - start))
    return rep

def dist(a,b):
    df = a-b
    return np.dot(df, df)


reps_archive_dir = "mikdb_rep_archive"

#nuoret_lst = [int(x) for x in open("idlist_nuoret_rajatettu_filtered", "r")]

# Done this way more slowly
rfiles_lst = [os.path.join(reps_archive_dir, x) for x in os.listdir(reps_archive_dir)]
              #if int(x.replace(".representations.npy", "")) in nuoret_lst]

# labels_lst, embeddings = [], []
#
# for path in rfiles_lst:
#     rff_arr = np.load(open(path, "r"))
#     #print(rff_arr)
#     label = os.path.split(path)[-1].replace(".representations.npy", "")
#     labels_lst += [label]
#     embeddings += [rff_arr]
#
# pickle.dump([labels_lst, embeddings],open("mikdb_all.pkl", "w"))

labels_lst, embeddings = pickle.load(open("mikdb_all.pkl", "r"))

print("FILES LOADED")
targetrep = getRep("t_photos/70.jpg")
tstart = time.time()
margin = 0.9

score_max = 0

for i in xrange(0, len(embeddings)):
    e = embeddings[i]
    score_local = sum(map(lambda x: 1-dist(targetrep, x), e))
    if(score_local>score_max):
        score_max = score_local
        print(labels_lst[i], score_max)
    # if(dst_avg <= margin):
    #     print("LABEL", labels_lst[i])
    #     print("With the probability of: {:0.2f}%".format((margin-dst_avg)/margin))
    #     print("==================================================================")

print("task finished in {} s".format(time.time()-tstart))