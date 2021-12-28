'''
PointGroup test.py
Written by Li Jiang
'''


import torch
import time
import numpy as np
import random
import os
from util.config import cfg
cfg.task = 'test'
from util.log import logger
import util.utils as utils
import util.eval as eval
from util_iou import *

import glob, plyfile, numpy as np, multiprocessing as mp, torch, json, argparse

import os,csv

# Map relevant classes to {0,1,...,19}, and ignored classes to -100
remapper = np.ones(150) * (-100)
#for i, x in enumerate([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 24, 28, 33, 34, 36, 39]):
#    remapper[x] = i

conf_thres=0.9




'''name2label={}
with open("/media/lzz/faef702d-ca59-4dad-a70a-089cc782183e1/pg/full/dataset/scannetv2/scannetv2-labels.combined.tsv") as fd:
    rd = csv.reader(fd, delimiter="\t", quotechar='"')
    start=1
    for row in rd:
        if start==1:
           start=0
           continue
        key=row[1]
        value=row[7]
        if value not in dic.keys():
            continue
        name2label[key]=value
        #print (key,value,dic[value])'''



def init():
    global result_dir
    result_dir = os.path.join(cfg.exp_path, 'result', 'epoch{}_nmst{}_scoret{}_npointt{}'.format(cfg.test_epoch, cfg.TEST_NMS_THRESH, cfg.TEST_SCORE_THRESH, cfg.TEST_NPOINT_THRESH), cfg.split)
    backup_dir = os.path.join(result_dir, 'backup_files')
    os.makedirs(backup_dir, exist_ok=True)
    os.makedirs(os.path.join(result_dir, 'predicted_masks'), exist_ok=True)
    os.system('cp test.py {}'.format(backup_dir))
    os.system('cp {} {}'.format(cfg.model_dir, backup_dir))
    os.system('cp {} {}'.format(cfg.dataset_dir, backup_dir))
    os.system('cp {} {}'.format(cfg.config, backup_dir))

    global semantic_label_idx
    semantic_label_idx = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 24, 28, 33, 34, 36, 39]

    logger.info(cfg)

    random.seed(cfg.test_seed)
    np.random.seed(cfg.test_seed)
    torch.manual_seed(cfg.test_seed)
    torch.cuda.manual_seed_all(cfg.test_seed)


def test(model, model_fn, data_name, epoch):
    logger.info('>>>>>>>>>>>>>>>> Start Evaluation >>>>>>>>>>>>>>>>')


    from data.scannetv2_inst import Dataset

    dataset = Dataset(test=True)
    path='train_cuda/'
    #print (path,'2222222222222')
    dataset.testLoader(path)
    #print ('1111111111111111')
    dataloader = dataset.test_data_loader

    intersection_meter = AverageMeter()
    union_meter = AverageMeter()
    target_meter = AverageMeter()
    
    try:
      os.mkdir('train'+str(conf_thres))
    except:
      pass
    try:
      os.mkdir('cnt'+str(conf_thres))
    except:
      pass
    
    with torch.no_grad():
        model = model.eval()
        start = time.time()

        matches = {}
        for i, batch in enumerate(dataloader):
            N = batch['feats'].shape[0]
            #print (N,'N')
            #test_scene_name = dataloader.test_file_names #[int(batch['id'][0])].split('/')[-1][:12]
            test_scene_name = dataset.test_file_names[int(batch['id'][0]/3)].split('/')[-1] #[:12] 
            #print (test_scene_name)
            #if os.path.exists('train_cuda/'+test_scene_name):
            #  continue

            start1 = time.time()
            preds = model_fn(batch, model, epoch)
            end1 = time.time() - start1
              
            semantic_scores=preds['Q'] #torch.argmax(preds['Q'],1).cpu().numpy()
            
            
            
            
            if i%3==0:
              semantic_acc=semantic_scores*0
            semantic_acc+=semantic_scores
            if i%3!=2:
              continue
            
            semantic_pred = semantic_acc.max(1)[1]  # (N) long, cuda
            semantic_pred=semantic_pred.detach().cpu().numpy()  #.cpu().numpy()   
            semantic_acc=semantic_acc.cpu().numpy()  
            
            
            
            
            raw_pred=preds['semantic']
            
            #print (semantic_pred.shape)
            #print (semantic_acc.shape) 
            semantic_acc=semantic_acc/3.0
            confs=np.max(semantic_acc,1) #[0] #preds['conf'].cpu().numpy()
            print (semantic_acc.shape, raw_pred.shape, confs.shape)
            
            #print (test_scene_name,'name')
            #scene=
            
            #fn='../../scannetv2/scannetv2/scans/'+test_scene_name+'/'+test_scene_name
                        

            #fn2 = fn[:-3] + 'labels.ply'
            #fn3 = fn + '_vh_clean_2.0.010000.segs.json'
            #fn4 = fn + '.aggregation.json'
            '''print(fn)
        
            f = plyfile.PlyData().read(fn+'_vh_clean_2.ply')
            points = np.array([list(x) for x in f.elements[0]])
            coords = np.ascontiguousarray(points[:, :3] - points[:, :3].mean(0))
            colors = np.ascontiguousarray(points[:, 3:6]) / 127.5 - 1'''
            print (test_scene_name)
            prev_data=torch.load('train_cuda//'+test_scene_name) #+'_inst.pth')
            #prev_data=torch.load('/home/lzz/sdc1/pg/multitask_iter1_e2e/train0.95//'+test_scene_name+'_inst_nostuff.pth')
            coords=prev_data[0]
            colors=prev_data[1]
            prev_sem=prev_data[2]
            prev_groups=prev_data[3]
            prev_seg=prev_data[4]
            #for c in prev_groups:
            #    for g in c:
            #        print (g)
            #        assert g in (np.unique(prev_seg))
            
            
            '''prev_point2seg=prev_seg
            prev_group_to_point = {}
            for j in range(len(prev_seg)):
              if prev_seg[j] not in prev_group_to_point:
                prev_group_to_point[prev_point2seg[j]] = []
              prev_group_to_point[prev_point2seg[j]].append(j)'''
                                                                        
            
            '''full_data=torch.load('/home/lzz/sdc1/pg/s3dis/train//'+test_scene_name.replace('_nostuff',''))
            full_sem=full_data[2]
            full_groups=full_data[3]
            #full_seg=full_data[4]
            #print (confs.shape, raw_pred.shape,'sssssssshape', full_sem.shape)
            assert raw_pred.shape[0]==full_sem.shape[0]'''
                                        



            '''fn3 = '/home/lzz/sdc1/scannetv2/scannetv2/scans/'+test_scene_name[:12]+'/'+test_scene_name[:12]+'_vh_clean_2.0.010000.segs.json'
            with open(fn3) as jsondata:
              d = json.load(jsondata)
              full_seg = d['segIndices']'''
            
            #print (prev_seg[:50])
            '''f=open('/media/lzz/faef702d-ca59-4dad-a70a-089cc782183e1/pg/full/dataset/scannetv2/s2.txt','w')
            for w in prev_seg:
                f.write(str(w)+'\n')
            f.close()
            #print (np.unique(full_seg), np.unique(prev_seg),'111111111111111111')
            assert np.array_equal(full_seg,prev_seg)'''           
            
        
            #f2 = plyfile.PlyData().read(fn2)
            '''with open(fn3) as jsondata:
                d = json.load(jsondata)
                seg = d['segIndices']'''
            
        
            point2seg=prev_seg
            group_to_point = {}
            for j in range(len(point2seg)):
              if point2seg[j] not in group_to_point:
                group_to_point[point2seg[j]] = []
              group_to_point[point2seg[j]].append(j)
              
            
            #np.save('../group_to_point/'+test_scene_name+'.npy',group_to_point)
            group_all=list(group_to_point.keys())
            group_all.sort()
            
            #print ('groupall',len(group_all))
        
        
            sem_labels = np.zeros((colors.shape[0],)) #remapper[np.array(f2.elements[0]['label'])]
            sem_labels[:]=-100
            groups=[]
            for i in range(13):
                groups.append([])
        
        
            cnt_group=0
            cnt=len(group_all)
            print (cnt, confs.shape)
            for i in range(cnt):
              
              conf=confs[i]
              
              c=semantic_pred[i]
              if conf<conf_thres:
                continue
              cnt_group+=1
              groups[c].append(group_all[i])
              idxs=group_to_point[group_all[i]]
              sem_labels[idxs]=c
        
        


        
            prev_group_cnt=0
            for g in range(len(prev_groups)):
              g2=prev_groups[g]
              prev_group_cnt+=len(g2)
              for i in g2:
                if (i not in groups[g]): # and (i in prev_group_to_point.keys()):
                   groups[g].append(i)
                   idxs=group_to_point[i]
                   sem_labels[idxs]=g
        
            '''full_group_cnt=0
            print (full_groups)
            for g in range(len(full_groups)):
              g2=full_groups[g]
              full_group_cnt+=len(g2)'''
        

            

            
            
            
            '''fcntnow=open('cnt'+str(conf_thres)+'/'+test_scene_name+'.txt','w')
            
            
            fcntnow.write(str(cnt_group)+' '+str(prev_group_cnt)+' '+str(full_group_cnt)+'\n')
            fcntnow.write(str(len(np.where(sem_labels!=-100)[0]))+' '+str(len(np.where(prev_sem!=-100)[0]))+' '+str(len(np.where(full_sem!=-100)[0])))
            
            fcntnow.close()'''
            
        
            
            print (len(np.where(sem_labels!=-100)[0]),len(np.where(prev_sem!=-100)[0]), prev_sem.shape[0])
            #print (cnt_group,prev_group_cnt,full_group_cnt)
            torch.save((coords, colors, sem_labels, groups, prev_seg), 'train_cuda/'+test_scene_name)


def non_max_suppression(ious, scores, threshold):
    ixs = scores.argsort()[::-1]
    pick = []
    while len(ixs) > 0:
        i = ixs[0]
        pick.append(i)
        iou = ious[i, ixs[1:]]
        remove_ixs = np.where(iou > threshold)[0] + 1
        ixs = np.delete(ixs, remove_ixs)
        ixs = np.delete(ixs, 0)
    return np.array(pick, dtype=np.int32)


if __name__ == '__main__':


    '''def test_fortrain(config, pretrain):
    import argparse
    import yaml
    import os
    parser = argparse.ArgumentParser(description='Point Cloud Segmentation')
    parser.add_argument('--config', type=str, default=config, help='path to config file')

    ### pretrain
    parser.add_argument('--pretrain', type=str, default=pretrain, help='path to pretrain model')
    args_cfg = parser.parse_args()
    #assert args_cfg.config is not None
    with open(config, 'r') as f:
        config = yaml.load(f)
    for key in config:
        for k, v in config[key].items():
            setattr(args_cfg, k, v)

    #return args_cfg


    cfg = args_cfg
    setattr(cfg, 'exp_path', os.path.join('exp', cfg.dataset, cfg.model_name, cfg.config.split('/')[-1][:-5]))'''


    init()

    ##### get model version and data version
    exp_name = cfg.config.split('/')[-1][:-5]
    model_name = exp_name.split('_')[0]
    data_name = exp_name.split('_')[-1]

    ##### model
    logger.info('=> creating model ...')
    logger.info('Classes: {}'.format(cfg.classes))

    if model_name == 'pointgroup':
        from model.pointgroup.pointgroup import PointGroup as Network
        from model.pointgroup.pointgroup import model_fn_decorator
    else:
        print("Error: no model version " + model_name)
        exit(0)
    model = Network(cfg)

    use_cuda = torch.cuda.is_available()
    logger.info('cuda available: {}'.format(use_cuda))
    assert use_cuda
    model = model.cuda()

    # logger.info(model)
    logger.info('#classifier parameters (model): {}'.format(sum([x.nelement() for x in model.parameters()])))

    ##### model_fn (criterion)
    model_fn = model_fn_decorator(test=True)

    ##### load model
    
    
    
    utils.checkpoint_restore(model, cfg.exp_path, cfg.config.split('/')[-1][:-5], use_cuda, cfg.test_epoch, dist=False, f=cfg.pretrain)      # resume from the latest epoch, or specify the epoch to restore

    ##### evaluate
    test(model, model_fn, data_name, cfg.test_epoch)
    