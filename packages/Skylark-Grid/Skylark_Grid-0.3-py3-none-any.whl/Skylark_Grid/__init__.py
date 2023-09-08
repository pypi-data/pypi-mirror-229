import os
import cv2
import numpy as np

class ImageMerger:
    def __init__(self, input_dir, output_dir, group_size=4, image_shape=(320, 320)):
        self.input_dir = input_dir
        self.output_dir = output_dir

        if not self.is_valid_group_size(group_size):
            raise ValueError("Invalid group size. It must have a specific square root value.")

        self.group_size = group_size
        self.image_shape = image_shape

        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

    def is_valid_group_size(self, group_size):
        # Check if the square root of the group_size is an integer
        sqrt_group_size = np.sqrt(group_size)
        return sqrt_group_size.is_integer()

    def load_annotations(self, txt_path, image_shape):
        with open(txt_path, 'r') as f:
            lines = f.readlines()
        annotations = []
        for line in lines:
            parts = line.strip().split()
            label = parts[0]
            x_center, y_center, width, height = map(float, parts[1:])

            # Calculate bounding box coordinates based on center
            x_min = int((x_center - width / 2) * image_shape[1])
            y_min = int((y_center - height / 2) * image_shape[0])
            x_max = int((x_center + width / 2) * image_shape[1])
            y_max = int((y_center + height / 2) * image_shape[0])
            annotations.append((label, x_min, y_min, x_max, y_max))
        return annotations

    def merge_images(self, image_files):
        merged_images = []
        annotations_list = []

        for image_file in image_files:
            image_path = os.path.join(self.input_dir, image_file)
            txt_file = os.path.splitext(image_file)[0] + ".txt"
            label_path = os.path.join(self.input_dir, txt_file)

            if not os.path.exists(label_path):
                print(f"Label file not found for {image_file}. Skipping.")
                continue

            image = cv2.imread(image_path)
            image = cv2.resize(image, self.image_shape)
            annotations = self.load_annotations(label_path, image.shape)
            annotations_list.append(annotations)
            merged_images.append(image)

        return merged_images, annotations_list

    def calculate_grid_dimensions(self):
        num_images = self.group_size
        num_cols = int(np.ceil(np.sqrt(num_images)))
        num_rows = (num_images + num_cols - 1) // num_cols
        return num_rows, num_cols

    def process_images(self):
        image_files = [f for f in os.listdir(self.input_dir) if f.lower().endswith(('.jpg', '.png'))]
        num_rows, num_cols = self.calculate_grid_dimensions()
        for i in range(0, len(image_files), self.group_size):
            image_group = image_files[i:i + self.group_size]

            merged_images, annotations_list = self.merge_images(image_group)

            while len(merged_images) < self.group_size:
                merged_images.append(np.zeros_like(merged_images[0]))  # Black placeholder

            grid_images = []

            for row in range(num_rows):
                row_images = merged_images[row * num_cols:(row + 1) * num_cols]
                row_merged = np.concatenate(row_images, axis=1)
                grid_images.append(row_merged)

            merged_image = np.concatenate(grid_images, axis=0)

            merged_annotations_path = os.path.join(self.output_dir, f"merged_{i // self.group_size}.txt")
            with open(merged_annotations_path, 'w') as f:
                for k, annotations in enumerate(annotations_list):
                    for annotation in annotations:
                        label, x_min, y_min, x_max, y_max = annotation

                        # Adjust coordinates based on the position of the images
                        if k >= num_cols:
                            y_min += merged_images[0].shape[0] * (k // num_cols)
                            y_max += merged_images[0].shape[0] * (k // num_cols)
                        if k % num_cols != 0:
                            x_min += merged_images[0].shape[1] * (k % num_cols)
                            x_max += merged_images[0].shape[1] * (k % num_cols)

                        # Append YOLO annotation to the file
                        image_width = merged_image.shape[1]
                        image_height = merged_image.shape[0]
                        x_center = (x_min + x_max) / (2.0 * image_width)
                        y_center = (y_min + y_max) / (2.0 * image_height)
                        width = (x_max - x_min) / image_width
                        height = (y_max - y_min) / image_height
                        yolo_annotation = f"{label} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n"
                        f.write(yolo_annotation)

            merged_image_path = os.path.join(self.output_dir, f"merged_{i // self.group_size}.jpg")
            cv2.imwrite(merged_image_path, merged_image)
            print(f"Merged annotations saved in YOLO format: {merged_annotations_path}")

