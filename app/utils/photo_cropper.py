import cv2
import os
from app.utils import smartcrop


class PhotoCropper:
    def crop_photo(self, file_path: tuple, output_dir) -> str:
        photos_dir, filename = file_path
        output_file = os.path.join(output_dir, f'cropped_{filename}')
        image = cv2.imread(os.path.join(photos_dir, filename))

        h, w, _ = image.shape
        is_portrait = h > w

        if is_portrait:
            fixed_width = 800
            if w > fixed_width:
                height_percent = fixed_width / float(w)
                height_size = int((float(h) * float(height_percent)))
                image = cv2.resize(image, (fixed_width, height_size))
        else:
            fixed_height = 800
            if h > fixed_height:
                height_percent = fixed_height / float(h)
                width_size = int((float(w) * float(height_percent)))
                image = cv2.resize(image, (width_size, fixed_height))

        safe_edge = 40
        target_width = 300
        target_height = round(target_width // (3/4))

        height, width, depth = image.shape

        if target_height > height:
            print('Warning: target higher than image')

        if target_width > width:
            print('Warning: target wider than image')

        matrix = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        center = smartcrop.center_from_faces(matrix)

        if not center:
            print('Using Good Feature Tracking method')
            center = smartcrop.center_from_good_features(matrix)

        print('Found center at', center)

        crop_pos = smartcrop.exact_crop(
            center, width, height, target_width, target_height)
        print('Crop rectangle is', crop_pos)

        cropped = image[int(crop_pos['top'] + safe_edge): int(crop_pos['bottom'] + safe_edge),
                        int(crop_pos['left']): int(crop_pos['right'])]

        cv2.imwrite(output_file, cropped)

        return output_file
