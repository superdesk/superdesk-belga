import {IExtension, IExtensionActivationResult, ISuperdesk, IArticle, ISubject} from 'superdesk-api';

type Scheme = 'media-credit' | 'belga-keywords' | 'countries';

const CVS: Array<Scheme> = ['media-credit', 'belga-keywords', 'countries'];

const DEFAULT_SUBJECT = {
    'media-credit': ['BELGA_ON_THE_SPOT'],
    'belga-keywords': ['RUSHES', 'BELGAILLUSTRATION', 'BELGAINTERVIEW', 'BELGAINSERT'],
    'countries': ['BEL'],
};

const extension: IExtension = {
    id: 'iptc',
    activate: (superdesk: ISuperdesk) => {
        console.info('activate');
        const result: IExtensionActivationResult = {
            contributions: {
                iptcMapping: (data, item: IArticle) => Promise.all<Array<ISubject>>(
                    CVS.map((id) => superdesk.entities.vocabulary.getVocabulary(id)),
                ).then((cvItems) => {
                    const subject: Array<ISubject> = [];
                    const items = {
                        'media-credit': cvItems[0],
                        'belga-keywords': cvItems[1],
                        'countries': cvItems[2],
                    };

                    for (let scheme of CVS) {
                        items[scheme]
                            .filter((subj) => DEFAULT_SUBJECT[scheme].includes(subj.qcode.toUpperCase()))
                            .forEach((subj) => {
                                subject.push({
                                    name: subj.name,
                                    qcode: subj.qcode,
                                    scheme: scheme,
                                    translations: subj.translations,
                                });
                            });
                    }

                    Object.assign(item, {
                        source: 'Belga',
                        subject: subject,
                        extra: {
                            city: data.City || 'Brussels',
                        },
                    });

                    console.debug('iptc', data, item);

                    return item;
                }),
            },
        };

        return Promise.resolve(result);
    },
};

export default extension;
