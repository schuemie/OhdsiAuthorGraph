import matplotlib.pyplot as plt
import matplotlib.transforms as transforms

def check_overlapping_boxes(bboxes):
    overlapping_pairs = []
    num_boxes = len(bboxes)
    for i in range(num_boxes):
        for j in range(i + 1, num_boxes):
            if bboxes[i].overlaps(bboxes[j]):
                overlapping_pairs.append((i, j))
    return overlapping_pairs

# Example usage
bbox1 = transforms.Bbox.from_extents(0, 0, 1, 1)
bbox2 = transforms.Bbox.from_extents(0.5, 0.5, 1.5, 1.5)
bbox3 = transforms.Bbox.from_extents(2, 2, 3, 3)

bboxes = [bbox1, bbox2, bbox3]

overlapping_pairs = check_overlapping_boxes(bboxes)
print("Overlapping bounding boxes (indices):", overlapping_pairs)