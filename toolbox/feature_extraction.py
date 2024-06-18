import os
from pathlib import Path
import numpy as np
from sklearn.mixture import GaussianMixture as GMM
from sklearn.decomposition import PCA

# Number of clusters for Gaussian mixture - k∈{1,...,K} where each Gaussian k has a μ (defining center), cov (definies
# width) and p(mixing probability)
K = 64
# Number of dimensions to reduce to w PCA
PCA_DIM = 64
# Number of samples to take to fit the GMM
SAMPLE_SIZE = 200000


def fisher_vector(xx, gmm):
    """
    Computes the fisher vector on a set of descriptors and GMM.

    :param xx: the descriptor (e.g. HOG/HOF/MBH) for each video.
    :type xx: array_like, shape (N, D) or (D, )
                The set of descriptors

    :param gmm: Gauassian mixture model of the descriptors.
    :type gmm: instance of sklearn mixture.GMM object

    :return: Fisher vector of the given descriptor.
    :rtype: array_like, shape (K + 2 * D * K ) where K is the number of GMM
            components and D is the dimension of each descriptor.

    This function was taken from this GitHub gist: https://gist.github.com/danoneata/9927923
    """
    xx = np.atleast_2d(xx)
    N = xx.shape[0]

    # Compute posterior probabilities.
    Q = gmm.predict_proba(xx)  # NxK

    # Compute the sufficient statistics of descriptors.
    Q_sum = np.sum(Q, 0)[:, np.newaxis] / N
    Q_xx = np.dot(Q.T, xx) / N
    Q_xx_2 = np.dot(Q.T, xx ** 2) / N

    # Compute derivatives with respect to mixing weights, means and variances.
    d_pi = Q_sum.squeeze() - gmm.weights_
    d_mu = Q_xx - Q_sum * gmm.means_
    d_sigma = (
        - Q_xx_2
        - Q_sum * gmm.means_ ** 2
        + Q_sum * gmm.covariances_
        + 2 * Q_xx * gmm.means_)

    # Merge derivatives into a vector.
    return np.hstack((d_pi, d_mu.flatten(), d_sigma.flatten()))

def read_descriptors(descriptors, index, gmm):
    """
        Extracts the trajectories (D=30), HOG (D=96), HOF (D=108) & MBH (D=192) from tracks.

        :param descriptors: the improved dense trajectories returned by
                            densetrack.densetrack method.
        :type descriptors: array_like, shape (N, ) where N is the number of
                           trajectories. Value of each element is a np.void.

        :param index: Index of the descriptor to be read
        :type index: list, with number of descriptor indices; or 'all' if iteration over all indices

        :return: combination of all descriptors
        :rtype: array_like, shape (N, D) where N is the number of
                      descriptors and D is the dimension
    """
    if index == 'all':
        # get all the descriptors & concatenate them to a 426dim array (see: https://hildekuehne.github.io/projects/end2end/kuehne_wacv16.pdf)
        trajectories = np.array([descriptors[i][-6] for i in
                                 range(descriptors.shape[0])])
        num_desc = descriptors.shape[0]
        trajectories_reshape = trajectories.reshape(num_desc, 30)
        hog_descriptors = np.array([descriptors[i][-5] for i in
                                    range(descriptors.shape[0])])
        hof_descriptor = np.array([descriptors[i][-4] for i in
                                   range(descriptors.shape[0])])
        mbh_x_descriptors = np.array([descriptors[i][-3] for i in
                                      range(descriptors.shape[0])])
        mbh_y_descriptors = np.array([descriptors[i][-2] for i in
                                      range(descriptors.shape[0])])
        combine = np.concatenate((trajectories_reshape, hog_descriptors), axis=1)
        combine = np.concatenate((combine, hof_descriptor), axis=1)
        combine = np.concatenate((combine, mbh_x_descriptors), axis=1)
        combine = np.concatenate((combine, mbh_y_descriptors), axis=1)
    else:
        #get the descriptors from the index list and concatenate them to an 426 dim array
        trajectories = np.array([descriptors[index[i]][-6] for i in
                                 range(len(index))])
        trajectories_reshape = trajectories.reshape(len(index),30)
        hog_descriptors = np.array([descriptors[index[i]][-5] for i in
                                 range(len(index))])
        hof_descriptor = np.array([descriptors[index[i]][-4] for i in
                                    range(len(index))])
        mbh_x_descriptors = np.array([descriptors[index[i]][-3] for i in
                                    range(len(index))])
        mbh_y_descriptors = np.array([descriptors[index[i]][-2] for i in
                                    range(len(index))])
        combine = np.concatenate((trajectories_reshape, hog_descriptors), axis=1)
        combine = np.concatenate((combine, hof_descriptor), axis=1)
        combine = np.concatenate((combine, mbh_x_descriptors), axis=1)
        combine = np.concatenate((combine, mbh_y_descriptors), axis=1)
        if combine.shape[0] > 63:
            combine = compute_PCA(combine)
        else:
            combine = np.zeros((64,64))
            print("Warning: FV derived from np.zeros - if done to often clustering is random")
        combine = fisher_vector(combine,gmm)
    return combine

def compute_PCA(descriptor,dim_PCA=PCA_DIM):
    '''
    Compute PCA of given descriptor

    :param descriptor: descriptor(s) that have to be reduced in dimensionality
    :type descriptor: array_like, shape (N, D) where N is the number of
                      descriptors and D is the dimension of each descriptor
                      (e.g. 96 for HOG).

    :param dim_PCA: Dimensions that PCA has to reduce descriptor(s) to
    :type dim_PCA: int value (for our purpose set to 64 as default
    :return: reduced descriptor
    '''
    descriptor_pca = PCA(n_components=int(dim_PCA)) \
        .fit(descriptor).transform(descriptor)
    return descriptor_pca

def compute_GMM(descriptor):
    '''
    Computes GMM for K components from features given by descriptor

    :param descriptor: The descriptors to fit the GMM with
    :type descriptor: array_like, shape (N, D) where N is the number of
                      descriptors and D is the dimension of each descriptor
                      (e.g. 96 for HOG).
    :return:  GMM
    '''
    #Get a random sample of SAMPLE_SIZE for creation of GMM
    if descriptor.shape[0] > SAMPLE_SIZE:
        rng = np.random.default_rng()
        sample = rng.choice(descriptor,SAMPLE_SIZE)
    else:
        sample = descriptor
    gmm = GMM(n_components=K, covariance_type='diag').fit(sample)
    return gmm

def power_normalize(xx, alpha=0.5):
    """Computes a alpha-power normalization for the matrix xx."""
    return np.sign(xx) * np.abs(xx) ** alpha


def L2_normalize(xx):
    """L2-normalizes each row of the data xx."""
    Zx = np.sum(xx * xx, 1)
    xx_norm = xx / np.sqrt(Zx[:, np.newaxis])
    xx_norm[np.isnan(xx_norm)] = 0
    return xx_norm

def normalize_fv(fv):
    '''
    Normalize the fisher vector with power & L2 normalization (power first see:
        https://lear.inrialpes.fr/pubs/2010/PSM10/PSM10_0766.pdf)
    :param fv: fisher vector of the descriptors
    :return: normalized fisher vector

    Functions from https://bitbucket.org/doneata/fv4a/src/9cd355701c1657eff11a71f8ce4cc42ddd381113/evaluate.py#lines-50:85
    '''
    power_norm = power_normalize(fv) #alpha value see: https://hal.inria.fr/hal-00830491v2/document
    l2_norm = L2_normalize(power_norm)
    return l2_norm

def extract_framewise_features(input_path, outputPath):
    ''''
    :param input_path: Absolute Path to IDT-Features data
    :type: String, giving location to a numpy file

    :param outputPath: folder to write framewise FV to
    :type: normalized, 64 dim fisher vector as .txt
    '''

    name = Path(input_path).stem
    tracks = np.load(input_path)
    '''
    Pipeline: 
    1) Compute DTFs & reduce dimensionality of the concatenated descriptors from 426 (30+96+108+192) to 64 w PCA
    2) Compute GMM w SAMPLE_SIZE samples from descriptors
    3) Compute which descriptor describes which frame in a dictionary
    4) Compute concatenated descriptor(s) for each frame
    5) Reduce dim of descriptors per frame to 64 
    6) Compute FV for each frame
    7) Reduce FV for each frame w PCA to 64 dim
    '''
    # Compute Concentrated Descriptors
    all_desc = read_descriptors(tracks, 'all', 'nothing')
    print("Descriptor Shape:", all_desc.shape)
    # Reduce Dim of Descriptors
    red_desc = compute_PCA(all_desc)
    # Compute GMM
    gmm = compute_GMM(red_desc)
    # index, which descriptor is looped over
    # dictionary - each key is a frame from the video,
    # each value is the index of the descriptors, which describe said frame
    dict_desc = {}
    for index in range(tracks.shape[0]):
        end_frame = tracks[index][0]
        frame_range = range(int(end_frame - 14), int(end_frame + 1))
        for j in frame_range:
            if j in dict_desc:
                dict_desc[j].append(index)
            else:
                dict_desc[j] = [index]
        index += 1
    # Frame-List - generate List with all descriptors per frame & reduce the descriptors to 64 dim
    # Compute FV for said frame
    frame_descriptors = []
    for key in dict_desc:
        indices = dict_desc.get(key)
        frame_descriptors.append(read_descriptors(tracks, indices, gmm))
    np_frame_descriptors = np.array(frame_descriptors)
    # Reduce to 64 dim
    np_frame_desc_red = compute_PCA(np_frame_descriptors)
    np.savetxt(os.path.join(outputPath, name
                            + '-frame_fv.txt'), np_frame_desc_red)

    del dict_desc
    del tracks
    return np_frame_desc_red



