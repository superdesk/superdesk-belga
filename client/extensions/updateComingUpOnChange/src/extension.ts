import {
    ISuperdesk,
    IExtension,
    IExtensionActivationResult,
    IArticle,
} from "superdesk-api";

const extension: IExtension = {
    id: "updateComingUpOnChange",
    activate: (superdesk: ISuperdesk) => {
        const result: IExtensionActivationResult = {
            contributions: {
                authoring: {
                    onUpdate: (current: IArticle, next: IArticle) => {
                        if (
                            next.extra?.DueBy === null ||
                            current.extra?.DueBy !== next.extra?.DueBy
                        ) {
                            return superdesk.dataApi
                                .patch("archive", current, { ...current, extra: next.extra })
                                .then((response) => {
                                    return Promise.resolve({
                                        ...next,
                                        _etag: response._etag,
                                    });
                                });
                        } else {
                            return Promise.resolve(next);
                        }
                    },
                },
            },
        };

        return Promise.resolve(result);
    },
};

export default extension;
