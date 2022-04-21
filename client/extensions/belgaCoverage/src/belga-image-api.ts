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

const parseCoverageId = (coverageId: string) => coverageId.split(':')[3];

export function getCoverageInfo(superdesk: ISuperdesk, coverageId: string, coverageProvider: string) : Promise<IBelgaCoverage> {
    return callApi<IBelgaCoverage>(superdesk, 'getGalleryById', {i: parseCoverageId(coverageId), provider: coverageProvider});
}

export function getCoverageImages(superdesk: ISuperdesk, coverageId: string, coverageProvider: string, max: number): Promise<Array<IBelgaImage>> {
    return callApi<Array<IBelgaImage>>(superdesk, 'getGalleryItems', {i: parseCoverageId(coverageId), provider: coverageProvider, n: '' + max});
}
