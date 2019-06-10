export interface IBelgaCoverage {
    description: string;
    iconThumbnailUrl: string;
}

export interface IBelgaImage {
    imageId: number;
    name: string;
    caption: string;
    gridUrl: string;
    previewUrl: string;
    thumbnailUrl: string;
}

const API_URL = 'https://api.ssl.belga.be/belgaimage-api/';

const callApi = (endpoint: string, params: {[key: string]: string}) => {
    const queryString = Object.keys(params).map((key) => `${key}=${params[key]}`).join('&');

    return fetch(API_URL + endpoint + '?' + queryString)
        .then((response) => response.json())
        .catch((reason) => {
            console.error('belga api error', reason);
            return Promise.reject(reason);
        });
};

const parseCoverageId = (coverageId: string) => coverageId.split(':')[3];

export function getCoverageInfo(coverageId: string) : Promise<IBelgaCoverage> {
    return callApi('getGalleryById', {i: parseCoverageId(coverageId)});
}

export function getCoverageImages(coverageId: string, max: number): Promise<Array<IBelgaImage>> {
    return callApi('getGalleryItems', {i: parseCoverageId(coverageId), n: '' + max});
}
