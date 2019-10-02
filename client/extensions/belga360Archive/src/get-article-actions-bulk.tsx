import { IArticle, ISuperdesk } from 'superdesk-api';
import { omit } from 'lodash';

interface IArticleArchive extends IArticle {
    mimetype: string;
}

export function getActionsBulkInitialize(superdesk: ISuperdesk) {
    const { gettext } = superdesk.localization;

    return function getActionsBulk(articles: Array<IArticleArchive>) {
        const omitProps = [
            '_created',
            '_etag',
            '_links',
            '_type',
            '_updated',
            'name',
            'selected',
            'ingest_provider',
            'fetch_endpoint',
        ];
        if (articles.some(article => article.mimetype !== 'application/vnd.belga.360archive')) {
            return Promise.resolve([]);
        }

        return Promise.resolve([
            {
                label: gettext('Import to Superdesk'),
                icon: 'icon-plus-large',
                onTrigger: () => {
                    superdesk.session.getCurrentUser().then(user => {
                        superdesk.dataApi
                            .create(
                                'archive',
                                articles.map(article => {
                                    article.task = {
                                        user: user._id,
                                        desk: '',
                                        stage: '',
                                    };
                                    return omit(article, omitProps);
                                })
                            )
                            .then(res => console.log(res))
                            .catch(err => console.error(err));
                    });
                },
            },
        ]);
    };
}
