import sys
sys.path += ['.']

from pytexutils.figures.image import image
from pytexutils.figures.tabular_image import tabular_image
import numpy as np
import os

if __name__ == '__main__':


    latex_image = image('fig1.png', caption='My image 1', label='img1', preamble=True)
    print(latex_image)


    images = np.array(
            [["fig1.png", "fig2.png"],["fig1.png", "fig2.png"]]
        )

    latex_images = tabular_image(images, caption='My image 1', label='img1', preamble=True)
    print(latex_images)

    save_folder = os.path.join('tmp', 'test_image')
    os.makedirs(save_folder, exist_ok=True)
    
    with open(os.path.join(save_folder, 'main-1.tex'), 'w') as texfile:
        texfile.writelines(latex_image)

    with open(os.path.join(save_folder, 'main-2.tex'), 'w') as texfile:
        texfile.writelines(latex_images)
