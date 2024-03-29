from io import BytesIO
import lmdb
from PIL import Image
import torch
from torch.utils.data import Dataset
from torchvision import transforms
import random
import data.util as Util
import numpy as np
import SimpleITK as sitk
from torch.utils import data
from scipy import ndimage as nd
import os
from tqdm import tqdm
def read_img(in_path):
    img_lit = []
    filenames = os.listdir(in_path)
    for f in tqdm(filenames):
        img = sitk.ReadImage(os.path.join(in_path, f))
        img_vol = sitk.GetArrayFromImage(img)
        img_lit.append(img_vol)
    return img_lit




class LIIFDataset(Dataset):
    def __init__(self, dataroot, datatype, l_resolution=16, r_resolution=128,  sample_q=None, gt_resize=None,augment=True, split='train', data_len=-1, need_LR=False):
        self.datatype = datatype
        self.l_res = l_resolution
        self.r_res = r_resolution
        self.data_len = data_len
        self.need_LR = need_LR
        self.split = split
        if split == "train":
            in_path_hr="./data_nii/hr_train"
        else:
            in_path_hr="./data_nii/hr_val"
        self.patch_hr = read_img(in_path=in_path_hr)

        # if datatype == 'lmdb':
        #     self.env = lmdb.open(dataroot, readonly=True, lock=False,
        #                          readahead=False, meminit=False)
        #     # init the datalen
        #     with self.env.begin(write=False) as txn:
        #         self.dataset_len = int(txn.get("length".encode("utf-8")))
        #     if self.data_len <= 0:
        #         self.data_len = self.dataset_len
        #     else:
        #         self.data_len = min(self.data_len, self.dataset_len)
        # elif datatype == 'img':
        #     self.sr_path = Util.get_paths_from_images(
        #         '{}/sr_{}_{}'.format(dataroot, l_resolution, r_resolution))
        #     self.hr_path = Util.get_paths_from_images(
        #         '{}/hr_{}'.format(dataroot, r_resolution))
        #     if self.need_LR:
        #         self.lr_path = Util.get_paths_from_images(
        #             '{}/lr_{}'.format(dataroot, l_resolution))
        #     self.dataset_len = len(self.hr_path)
        #     if self.data_len <= 0:
        #         self.data_len = self.dataset_len
        #     else:
        #         self.data_len = min(self.data_len, self.dataset_len)
        # else:
        #     raise NotImplementedError(
        #         'data_type [{:s}] is not recognized.'.format(datatype))

    def __len__(self):
        return len(self.patch_hr)

    def __getitem__(self, index):
        # img_HR = None
        # img_LR = None
        patch_hr = self.patch_hr[index]
        s = 2
        patch_lr = nd.interpolation.zoom(patch_hr, 1 / s, order=3)
        # if self.datatype == 'lmdb':
        #     with self.env.begin(write=False) as txn:
        #         hr_img_bytes = txn.get(
        #             'hr_{}_{}'.format(
        #                 self.r_res, str(index).zfill(5)).encode('utf-8')
        #         )
        #         sr_img_bytes = txn.get(
        #             'sr_{}_{}_{}'.format(
        #                 self.l_res, self.r_res, str(index).zfill(5)).encode('utf-8')
        #         )
        #         if self.need_LR:
        #             lr_img_bytes = txn.get(
        #                 'lr_{}_{}'.format(
        #                     self.l_res, str(index).zfill(5)).encode('utf-8')
        #             )
        #         # skip the invalid index
        #         while (hr_img_bytes is None) or (sr_img_bytes is None):
        #             new_index = random.randint(0, self.data_len-1)
        #             hr_img_bytes = txn.get(
        #                 'hr_{}_{}'.format(
        #                     self.r_res, str(new_index).zfill(5)).encode('utf-8')
        #             )
        #             sr_img_bytes = txn.get(
        #                 'sr_{}_{}_{}'.format(
        #                     self.l_res, self.r_res, str(new_index).zfill(5)).encode('utf-8')
        #             )
        #             if self.need_LR:
        #                 lr_img_bytes = txn.get(
        #                     'lr_{}_{}'.format(
        #                         self.l_res, str(new_index).zfill(5)).encode('utf-8')
        #                 )
        #         img_HR = Image.open(BytesIO(hr_img_bytes)).convert("RGB")
        #         img_SR = Image.open(BytesIO(sr_img_bytes)).convert("RGB")
        #         if self.need_LR:
        #             img_LR = Image.open(BytesIO(lr_img_bytes)).convert("RGB")
        # else:
        #     img_HR = Image.open(self.hr_path[index]).convert("RGB")
        #     img_SR = Image.open(self.sr_path[index]).convert("RGB")
        #     if self.need_LR:
        #         img_LR = Image.open(self.lr_path[index]).convert("RGB")
        # if self.need_LR:
        #     [img_LR, img_SR, img_HR] = Util.transform_augment(
        #         [img_LR, img_SR, img_HR], split=self.split, min_max=(-1, 1))
        #     return {'LR': img_LR, 'HR': img_HR, 'SR': img_SR, 'Index': index}
        # else:
        #     [img_SR, img_HR] = Util.transform_augment(
        #         [img_SR, img_HR], split=self.split, min_max=(-1, 1))
        patch_hr = torch.tensor(patch_hr).float().unsqueeze(0)
        patch_lr = torch.tensor(patch_lr).float().unsqueeze(0)

        return {'inp': patch_lr, 'gt': patch_hr}
    #     self.datatype = datatype
    #     self.l_res = l_resolution
    #     self.r_res = r_resolution
    #     self.data_len = data_len
    #     self.need_LR = need_LR
    #     self.split = split
    #     self.augment = augment
    #     self.gt_resize = gt_resize
    #     self.sample_q = sample_q
    #     if datatype == 'lmdb':
    #         self.env = lmdb.open(dataroot, readonly=True, lock=False,
    #                              readahead=False, meminit=False)
    #         # init the datalen
    #         with self.env.begin(write=False) as txn:
    #             self.dataset_len = int(txn.get("length".encode("utf-8")))
    #         if self.data_len <= 0:
    #             self.data_len = self.dataset_len
    #         else:
    #             self.data_len = min(self.data_len, self.dataset_len)
    #     elif datatype == 'img':
    #         # self.sr_path = Util.get_paths_from_images(
    #         #     '{}/sr_{}_{}'.format(dataroot, l_resolution, r_resolution))
    #         self.hr_path = Util.get_paths_from_images(
    #             '{}/hr_{}'.format(dataroot, r_resolution))
    #         if self.need_LR:
    #             self.lr_path = Util.get_paths_from_images(
    #                 '{}/lr_{}'.format(dataroot, l_resolution))
    #         self.dataset_len = len(self.hr_path)
    #         if self.data_len <= 0:
    #             self.data_len = self.dataset_len
    #         else:
    #             self.data_len = min(self.data_len, self.dataset_len)
    #     else:
    #         raise NotImplementedError(
    #             'data_type [{:s}] is not recognized.'.format(datatype))

    # def __len__(self):
    #     return self.data_len

    # def __getitem__(self, index):

    #     if self.datatype == 'lmdb':
    #         with self.env.begin(write=False) as txn:
    #             hr_img_bytes = txn.get(
    #                 'hr_{}_{}'.format(
    #                     self.r_res, str(index).zfill(5)).encode('utf-8')
    #             )
    #             sr_img_bytes = txn.get(
    #                 'sr_{}_{}_{}'.format(
    #                     self.l_res, self.r_res, str(index).zfill(5)).encode('utf-8')
    #             )
    #             if self.need_LR:
    #                 lr_img_bytes = txn.get(
    #                     'lr_{}_{}'.format(
    #                         self.l_res, str(index).zfill(5)).encode('utf-8')
    #                 )
    #             # skip the invalid index
    #             while (hr_img_bytes is None) or (sr_img_bytes is None):
    #                 new_index = random.randint(0, self.data_len-1)
    #                 hr_img_bytes = txn.get(
    #                     'hr_{}_{}'.format(
    #                         self.r_res, str(new_index).zfill(5)).encode('utf-8')
    #                 )
    #                 sr_img_bytes = txn.get(
    #                     'sr_{}_{}_{}'.format(
    #                         self.l_res, self.r_res, str(new_index).zfill(5)).encode('utf-8')
    #                 )
    #                 if self.need_LR:
    #                     lr_img_bytes = txn.get(
    #                         'lr_{}_{}'.format(
    #                             self.l_res, str(new_index).zfill(5)).encode('utf-8')
    #                     )
    #             img_HR = Image.open(BytesIO(hr_img_bytes)).convert("RGB")
    #             img_SR = Image.open(BytesIO(sr_img_bytes)).convert("RGB")
    #             if self.need_LR:
    #                 img_LR = Image.open(BytesIO(lr_img_bytes)).convert("RGB")
    #     else:
    #         img_hr = Image.open(self.hr_path[index]).convert("RGB")
    #         if self.need_LR:
    #             img_lr = Image.open(self.lr_path[index]).convert("RGB")
    #         img_hr, img_lr = transforms.ToTensor()(img_hr), transforms.ToTensor()(img_lr)
    #     if self.augment:
    #         if random.random() < 0.5:
    #             img_lr = img_lr.flip(-1)
    #             img_hr = img_hr.flip(-1)
    #     if self.gt_resize is not None:
    #         img_hr = Util.resize_fn(img_hr, self.gt_resize)

    #     return {
    #     'inp': img_lr,

    #     'gt': img_hr}

