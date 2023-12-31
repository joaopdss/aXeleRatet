import random
import numpy as np
from axelerate.anchor_generator.preprocessing import parse_annotation
import json

def IOU(ann, centroids):
	w, h = ann
	similarities = []

	for centroid in centroids:
		c_w, c_h = centroid

		if c_w >= w and c_h >= h:
			similarity = w*h/(c_w*c_h)
		elif c_w >= w and c_h <= h:
			similarity = w*c_h/(w*h + (c_w-w)*c_h)
		elif c_w <= w and c_h >= h:
			similarity = c_w*h/(w*h + c_w*(c_h-h))
		else: #means both w,h are bigger than c_w and c_h respectively
			similarity = (c_w*c_h)/(w*h)
		similarities.append(similarity) # will become (k,) shape

	return np.array(similarities)

def avg_IOU(anns, centroids):
	n,d = anns.shape
	sum = 0.

	for i in range(anns.shape[0]):
		sum+= max(IOU(anns[i], centroids))

	return sum/n

def print_get_anchors(centroids):
	anchors = centroids.copy()

	widths = anchors[:, 0]
	sorted_indices = np.argsort(widths)
	anchor_list = []
	
	r = "anchors: ["
	for i in sorted_indices[:-1]:
		r += '%0.5f,%0.5f, ' % (anchors[i,0], anchors[i,1])
		anchor_list.append(anchors[i, 0])
		anchor_list.append(anchors[i, 1])

	#there should not be comma after last anchor, that's why
	r += '%0.5f,%0.5f' % (anchors[sorted_indices[-1:],0], anchors[sorted_indices[-1:],1])
	r += "]"
	anchor_list.append(anchors[sorted_indices[-1:], 0][0])
	anchor_list.append(anchors[sorted_indices[-1:], 1][0])

	print(r)
	return anchor_list

def run_kmeans(ann_dims, anchor_num, show):
	ann_num = ann_dims.shape[0]
	iterations = 0
	prev_assignments = np.ones(ann_num)*(-1)
	iteration = 0
	old_distances = np.zeros((ann_num, anchor_num))
	
	if show:
		print(ann_dims)
	indices = [random.randrange(ann_dims.shape[0]) for i in range(anchor_num)]
	centroids = ann_dims[indices]
	anchor_dim = ann_dims.shape[1]

	while True:
		distances = []
		iteration += 1
		for i in range(ann_num):
			d = 1 - IOU(ann_dims[i], centroids)
			distances.append(d)
		distances = np.array(distances) # distances.shape = (ann_num, anchor_num)

		print("iteration {}: dists = {}".format(iteration, np.sum(np.abs(old_distances-distances))))

		#assign samples to centroids
		assignments = np.argmin(distances,axis=1)

		if (assignments == prev_assignments).all() :
			return centroids

		#calculate new centroids
		centroid_sums=np.zeros((anchor_num, anchor_dim), np.float)
		for i in range(ann_num):
			centroid_sums[assignments[i]]+=ann_dims[i]
		for j in range(anchor_num):
			centroids[j] = centroid_sums[j]/(np.sum(assignments==j) + 1e-6)

		prev_assignments = assignments.copy()
		old_distances = distances.copy()

def generate_anchors(config, num_anchors=5, show=False):
	train_imgs, train_labels = parse_annotation(config['train']['train_annot_folder'],
												config['train']['train_image_folder'],
												config['model']['labels'])
	grid_w = config['model']['input_size']/32
	grid_h = config['model']['input_size']/32

	# run k_mean to find the anchors
	annotation_dims = []
	for image in train_imgs:
		cell_w = image['width']/grid_w
		cell_h = image['height']/grid_h

		for obj in image['object']:
			relative_w = (float(obj['xmax']) - float(obj['xmin']))/cell_w
			relatice_h = (float(obj["ymax"]) - float(obj['ymin']))/cell_h
			annotation_dims.append(tuple(map(float, (relative_w,relatice_h))))

	annotation_dims = np.array(annotation_dims)
	centroids = run_kmeans(annotation_dims, num_anchors, show)

	# write anchors to file
	# print('\naverage IOU for', num_anchors, 'anchors:', '%0.2f' % avg_IOU(annotation_dims, centroids))
	anchors_ret = print_get_anchors(centroids)
	return anchors_ret