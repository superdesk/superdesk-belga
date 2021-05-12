import {IExtension, IExtensionActivationResult, ISuperdesk, IArticle, ISubject} from 'superdesk-api';

type Scheme = 'media-source' | 'belga-keywords' | 'country' | 'services-products' | 'distribution';

const CVS: Array<Scheme> = ['media-source', 'belga-keywords', 'country', 'services-products', 'distribution'];

const DEFAULT_SUBJECT = {
    'media-source': ['BELGA_ON_THE_SPOT'],
    'belga-keywords': ['RUSHES', 'BELGAILLUSTRATION', 'BELGAINTERVIEW', 'BELGAINSERT'],
    'country': ['COUNTRY_BEL'],
    'distribution': ['BILINGUAL'],
    'services-products': ['BIN/ALG', 'INT/GEN'],
};

const COPY_FROM_PARENT_SCHEMAS = [
    'belga-keywords',
    'services-products', // Packages
];

const extension: IExtension = {
    activate: (superdesk: ISuperdesk) => {
        const result: IExtensionActivationResult = {
            contributions: {
                iptcMapping: (data, item: IArticle, parent?: IArticle) => Promise.all<Array<ISubject>>(
                    CVS.map((id) => superdesk.entities.vocabulary.getVocabulary(id)),
                ).then((cvItems) => {
                    const subject: Array<ISubject> = [];
                    const nextItem = Object.assign({}, item);

                    CVS.forEach((scheme, index) => {
                        if (cvItems[index] == null) {
                            console.warn('missing CV', scheme);
                            return;
                        }

                        cvItems[index]
                            .filter((subj) => DEFAULT_SUBJECT[scheme].includes(subj.qcode.toUpperCase()))
                            .forEach((subj) => {
                                subject.push({
                                    name: subj.name,
                                    qcode: subj.qcode,
                                    scheme: scheme,
                                    translations: subj.translations,
                                    source: '',
                                });
                            });
                    });

                    Object.assign(nextItem, {
                        language: 'nl',
                        source: 'Belga',
                        subject: subject,
                        extra: {
                            city: data.City || 'Brussels',
                        },
                    });

                    if (parent != null) { // copy metadata from parent
                        const parentSubject = parent.subject || [];

                        for (let scheme of COPY_FROM_PARENT_SCHEMAS) {
                            const parentSubjectItems = parentSubject.filter((subj) => subj.scheme === scheme);

                            if (parentSubjectItems.length) {
                                item.subject = subject.filter((subj) => subj.scheme === scheme)
                                    .concat(parentSubjectItems);
                            }
                        }

                        Object.assign(nextItem, {
                            language: parent.language,
                            slugline: parent.slugline,
                            headline: parent.headline,
                            authors: parent.authors,
                            keywords: parent.keywords,
                        });
                    }

                    return nextItem;
                }),
            },
        };

        return Promise.resolve(result);
    },
};

export default extension;
