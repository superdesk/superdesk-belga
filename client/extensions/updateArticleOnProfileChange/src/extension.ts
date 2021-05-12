import {
    ISuperdesk,
    IExtension,
    IExtensionActivationResult,
    IArticle,
    ISubject,
} from 'superdesk-api';

const extension: IExtension = {
    activate: (superdesk: ISuperdesk) => {
        const result: IExtensionActivationResult = {
            contributions: {
                authoring: {
                    onUpdateBefore: (current: IArticle, next: IArticle) => {
                        if (current.profile == null || next.profile == null) {
                            return Promise.resolve(next);
                        }
                        return Promise.all([
                            superdesk.entities.contentProfile.get(current.profile),
                            superdesk.entities.contentProfile.get(next.profile),
                        ]).then((res) => {
                            const [currentProfile, nextProfile] = res;

                            if (currentProfile.label === 'ALERT' && nextProfile.label !== 'ALERT') {
                                return Promise.resolve({
                                    ...next,
                                    urgency: 3,
                                    subject: (next.subject ?? [])
                                        .filter((item: ISubject) => item?.scheme !== 'distribution')
                                        .concat({
                                            qcode: 'default',
                                            name: 'default',
                                            scheme: 'distribution',
                                            source: '',
                                        }),
                                });
                            } else if (currentProfile.label !== 'ALERT' && nextProfile.label === 'ALERT') {
                                return Promise.resolve({
                                    ...next,
                                    urgency: 1,
                                    subject: (next.subject ?? [])
                                        .filter((item: ISubject) => item?.scheme !== 'distribution')
                                        .concat({
                                            qcode: 'bilingual',
                                            name: 'bilingual',
                                            scheme: 'distribution',
                                            source: '',
                                        }),
                                });
                            } else {
                                return Promise.resolve(next);
                            }
                        });
                    },
                },
            },
        };

        return Promise.resolve(result);
    },
};

export default extension;
