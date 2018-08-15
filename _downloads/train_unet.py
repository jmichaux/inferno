"""
Train UNet Example
================================

This example should illustrate how to use the trainer class
in conjunction with a unet, we use a toy dataset here

"""


import torch.nn as nn
from inferno.io.box.binary_blobs import get_binary_blob_loaders
from inferno.trainers.basic import Trainer
from inferno.extensions.layers.building_blocks import ResBlock
from inferno.extensions.layers.unet import ResBlockUNet
from inferno.extensions.layers.unet import foo
from inferno.utils.torch_utils import unwrap
from inferno.utils.python_utils import ensure_dir
import pylab



# change directories to your needs
LOG_DIRECTORY = ensure_dir('log')
SAVE_DIRECTORY = ensure_dir('save')
DATASET_DIRECTORY = ensure_dir('dataset')

# should cuda be used
USE_CUDA = True

# Build a residual unet where the last layer is not activated
model = nn.Sequential(
    ResBlock(dim=2, in_channels=1, out_channels=5),
    ResBlockUNet(dim=2, in_channels=5, out_channels=2,  activated=False) 
)
train_loader, test_loader, validate_loader = get_binary_blob_loaders(
    train_batch_size=3,
    length=512, # <= size of the images
)

# Build trainer
trainer = Trainer(model)
trainer.build_criterion('CrossEntropyLoss')
trainer.build_metric('IOU')
trainer.build_optimizer('Adam')
trainer.validate_every((10, 'epochs'))
trainer.save_every((10, 'epochs'))
trainer.save_to_directory(SAVE_DIRECTORY)
trainer.set_max_num_epochs(40)

# Bind loaders
trainer.bind_loader('train', train_loader) 
trainer.bind_loader('validate', validate_loader)

if USE_CUDA:
    trainer.cuda()

# Go!
trainer.fit()


# predict:
trainer.load(best=True)
trainer.bind_loader('train', train_loader)
trainer.bind_loader('validate', validate_loader)
trainer.eval_mode()

if USE_CUDA:
    trainer.cuda()

# look at an example
for x,y in test_loader:
    if USE_CUDA:
        x = x.cuda()
    yy = trainer.apply_model(x)
    yy = nn.functional.softmax(yy,dim=1)
    yy = unwrap(yy, as_numpy=True, to_cpu=True)
    x  = unwrap(x,  as_numpy=True, to_cpu=True)
    y  = unwrap(y, as_numpy=True, to_cpu=True)

    batch_size = yy.shape[0]
    for b in range(batch_size):

        fig = pylab.figure()
        ax1 = fig.add_subplot(1,3,1)
        ax1.imshow(x[b,0,...])
        ax2 = fig.add_subplot(1,3,2)
        ax2.imshow(y[b,...])
        ax3 = fig.add_subplot(1,3,3)
        ax3.imshow(yy[b,1,...])

        pylab.show()

    break
