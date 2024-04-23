import {
    ISuperdesk,
    IExtension,
    IExtensionActivationResult,
} from 'superdesk-api';

const extension: IExtension = {
    activate: (superdesk: ISuperdesk) => {
        const result: IExtensionActivationResult = {
            contributions: {
                aiAssistant: {
                    generateHeadlines: (article) => {
                        return superdesk.entities.contentProfile.get(article.profile).then((profile) => {
                            return superdesk.httpRequestJsonLocal<{response: Array<string>}>({
                                method: 'POST',
                                path: '/belga/ai/toolkit/headlines',
                                payload: {
                                    text: article.body_html,
                                    nrTitles: 3,
                                    maxCharacters: profile.schema['headline']?.maxlength ?? 0,
                                }
                            }).then((result) => result.response)
                        });
                    },
                    generateSummary: (article) => {
                        return superdesk.entities.contentProfile.get(article.profile).then((profile) => {
                            return superdesk.httpRequestJsonLocal<{response: string}>({
                                method: 'POST',
                                path: '/belga/ai/toolkit/summarize',
                                payload: {
                                    text: article.body_html,
                                    maxCharacters: profile.schema['body_html']?.maxlength ?? 0,
                                }
                            }).then((result) => result.response)
                        });
                    },
                },
            },
        };

        return Promise.resolve(result);
    },
};

export default extension;
