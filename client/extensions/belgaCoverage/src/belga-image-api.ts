import { ISuperdesk } from "superdesk-api";

export interface IBelgaCoverage {
    name: string;
    /** total number of images in the coverage */
    nrImages: number;
    createDate: string;
    description: string;
    iconThumbnailUrl: string;
}

export interface IBelgaImage {
    imageId: number;
    name: string;
    caption: string;
    gridUrl: string;
    smallUrl: string;
    previewUrl: string;
    thumbnailUrl: string;
}

function callApi<T>(superdesk: ISuperdesk, endpoint: string, params: {[key: string]: string}): Promise<T> {
    return superdesk.dataApi.queryRawJson<T>(`belga_image_api/${endpoint}`, params)
        .catch((reason) => {
            console.error('belga api error', reason);
            return Promise.reject(reason);
        });
}

export function getCoverageInfo(superdesk: ISuperdesk, coverageId: string) : Promise<IBelgaCoverage> {
    return callApi<IBelgaCoverage>(superdesk, 'getGalleryById', {i: coverageId});
}

export function getCoverageImages(superdesk: ISuperdesk, coverageId: string, max: number): Promise<Array<IBelgaImage>> {
    return callApi<Array<IBelgaImage>>(superdesk, 'getGalleryItems', {i: coverageId, n: '' + max});
}
