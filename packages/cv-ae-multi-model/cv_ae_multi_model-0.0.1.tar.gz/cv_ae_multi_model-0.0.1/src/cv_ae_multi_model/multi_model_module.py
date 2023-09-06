import logging
import os
import time
import torch
import timm
from timm.data import resolve_data_config
from timm.data.transforms_factory import create_transform
from torch import nn

class MultiModelModule(nn.Module):
    def __init__(self, net_name_arg=[], num_class_arg=[], device="cpu"):
        super().__init__()
        logging.info("Initializing Multi Model Module...")

        self.models = {}

        for i, (net_name, num_class) in enumerate(zip(net_name_arg, num_class_arg)):
            neti = "net_" + str(i+1)
            self.models[neti] = timm.create_model(net_name, pretrained=False, num_classes=num_class)

        self.device = device



    def forward(self, image_urls):

        model_outputs = torch.Tensor().to(self.device)

        for neti, net in self.models.items():

            output = net(image_urls)
            probabilities = torch.nn.functional.softmax(output, dim=1)
            max_prob_idx = torch.max(probabilities,1, keepdim=True)[0]
            mask = ~probabilities.ge(max_prob_idx)
            probabilities[mask] = 0
            model_outputs = torch.concat((model_outputs, probabilities), 1)


        return model_outputs


    def build_transforms(self):

        neti = self.models["net_1"]
        config = resolve_data_config({}, model=neti)
        transform = create_transform(**config, is_training=False)
        return transform
