import os
import time
import openface
import cv2
import pickle
import json

import numpy as np

__author__ = 'voldemarich'

openface_model_dir = "/home/voldemarich/myinstall/openface/models"
dlib_model_path = os.path.join(openface_model_dir, "dlib", "shape_predictor_68_face_landmarks.dat")
openface_model_path = os.path.join(openface_model_dir, "openface", "nn4.small2.v1.t7")

std_img_dimension = 96  # aligning faces to imgs of (std_img_dimension x std_img_dimension) size

align = openface.AlignDlib(dlib_model_path)
net = openface.TorchNeuralNet(openface_model_path, std_img_dimension)
verbose = False
print("LOADED LIBS")

def getReps(imgPath):
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

    bbs = align.getAllFaceBoundingBoxes(rgbImg)
    if bbs is None:
        raise Exception("Unable to find a face: {}".format(imgPath))
    if verbose:
        print("Face detection took {} seconds.".format(time.time() - start))

    reps_arr = []
    for bb in bbs:
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
        reps_arr += [rep]
    return reps_arr

def dist(a,b):
    df = a-b
    return np.dot(df, df)


#reps_archive_dir = "mikdb_rep_archive"

#nuoret_lst = [int(x) for x in open("idlist_nuoret_rajatettu_filtered", "r")]

# Done this way more slowly
#rfiles_lst = [os.path.join(reps_archive_dir, x) for x in os.listdir(reps_archive_dir)]
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

labels_lst, embeddings = pickle.load(open("../recognition_stuff/mikdb_all.pkl", "r"))

print("FILES LOADED")

workdir = "neural_photos"
id_db = json.load(open("../recognition_stuff/database.json", "r"))
os.chdir(workdir)


while True:
    try:
        toprocess = [(x[0], time.ctime(x[1].st_ctime)) for x in sorted([(fn, os.stat(fn)) for fn in os.listdir(".")], key = lambda x: x[1].st_ctime)]
        for entry in toprocess:
            targetreps = getReps(entry[0])
            tstart = time.time()

            score_max = 0

            candidates = []
            if len(targetreps) < 1: continue
            for rep in targetreps:
                cand_local = []
                for i in xrange(0, len(embeddings)):
                    e = embeddings[i]
                    score_local = sum(map(lambda x: 1-dist(rep, x), e))/len(e)
                    if(score_local>score_max):
                        score_max = score_local
                        cand_local += [id_db[labels_lst[i]]["name"]]
                if len(candidates) > 2:
                    cand_local = candidates[-1:]
                candidates += cand_local

            try:
                pl = float(entry[0][:entry[0].index("_")])
            except:
                pl = 80
            print("The image done. Pulse rate on it was {}".format(pl))
            print("The possible people on the image (of known in database) are:")
            for i in candidates:
                print(i)
            print ("============================================================")
            os.remove(entry[0])


                    #print(labels_lst[i], score_max)
                # if(dst_avg <= margin):
                #     print("LABEL", labels_lst[i])
                #     print("With the probability of: {:0.2f}%".format((margin-dst_avg)/margin))
                #     print("==================================================================")

            #print("task finished in {} s".format(time.time()-tstart))
    except KeyboardInterrupt:
        break
        print("successfully finished")