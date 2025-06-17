import * as React from 'react';
import angular from 'angular';

import {IUser, IArticle, ISuperdesk} from 'superdesk-api';
import {startApp} from 'superdesk-core/scripts/index';
import {AvatarContentText} from 'superdesk-ui-framework';

import belgaImage from './belga/image';
import belga360Archive from './belga/360archive';
import belgaPress from './belga/belgapress';
import moment from 'moment';
import {IEventItem, IPlanningItem} from 'superdesk-planning/client/interfaces';
import {setCoverageDueDateStrategy} from 'superdesk-planning/client/configure';
import {eventUtils} from 'superdesk-planning/client/utils';

class UserAvatar extends React.PureComponent<{user: Partial<IUser>}> {
    render() {
        if (this.props.user.sign_off == null) { // will be null when creating a new user
            return null;
        } else {
            return (
                <AvatarContentText
                    text={this.props.user.sign_off}
                    tooltipText={this.props.user.display_name}
                />
            );
        }
    }
}

/**
 * Offset is needed because belga ai sometimes doesn't respect the maxCharacter length and outputs 4/5 more characters.
 */
const MAX_CHARACTER_OFFSET = 10;

function getCoverageDueDate(
    planningItem: IPlanningItem,
    eventItem?: IEventItem,
): moment.Moment | null {
    let coverageTime: moment.Moment | null = null;

    if (eventItem && eventUtils.isEventAllDay(eventItem.dates?.start, eventItem.dates?.end, true)) {
        coverageTime = moment(eventItem.dates?.end);
        coverageTime.set('hour', 20);
        coverageTime.set('minute', 0);
        coverageTime.set('second', 0);
    } else if (eventItem) {
        coverageTime = moment(eventItem.dates?.end);
        coverageTime.add(1, 'hour');
        if (eventItem.dates?.end && !coverageTime.isSame(eventItem.dates?.end, 'day')) {
            // make sure we're not going into the next day
            coverageTime = moment(eventItem.dates?.end);
        }
    } else if (planningItem) {
        coverageTime = moment(planningItem.planning_date);
    }

    return coverageTime;
}

setCoverageDueDateStrategy(getCoverageDueDate);

setTimeout(() => {
    startApp([
        {
            id: 'planning-extension',
            load: () => import('superdesk-planning/client/planning-extension'),
        },
        {
            id: 'markForUser',
            load: () => import('superdesk-core/scripts/extensions/markForUser'),
        },
        {
            id: 'datetimeField',
            load: () => import('superdesk-core/scripts/extensions/datetimeField'),
        },
        {
            id: 'belgaCoverage',
            load: () => import('./extensions/belgaCoverage'),
        },
        {
            id: 'updateArticleOnProfileChange',
            load: () => import('./extensions/updateArticleOnProfileChange'),
        },
        {
            id: 'saveArticleOnComingUpChange',
            load: () => import('./extensions/saveArticleOnComingUpChange'),
        },
        {
            id: 'iptc',
            load: () => import('./extensions/iptc'),
        },
        {
            id: 'ai-widget',
            load: () => import('superdesk-core/scripts/extensions/ai-widget').then((widget) => {
                widget.configure((superdesk: ISuperdesk) => ({
                    translations: {
                        translateActionIntegration: true,
                        generateTranslations: (article: IArticle, language: string) => {
                            return superdesk.httpRequestJsonLocal<{response: Array<string>}>({
                                method: 'POST',
                                path: '/belga/ai/toolkit/translate',
                                payload: {
                                    language: language,
                                    text: article.body_html,
                                }
                            }).then((result) => result.response)
                        },
                    },
                    generateHeadlines: (article: IArticle) => {
                        const profile = superdesk.entities.contentProfile.get(article.profile);
                        const maxCharacterLength = profile.schema['headline']?.maxlength;

                        return superdesk.httpRequestJsonLocal<{response: Array<string>}>({
                            method: 'POST',
                            path: '/belga/ai/toolkit/headlines',
                            payload: {
                                text: article.body_html,
                                nrTitles: 3,
                                maxCharacters: maxCharacterLength != null
                                ? (maxCharacterLength - MAX_CHARACTER_OFFSET)
                                : 0,
                            }
                        }).then((result) => result.response)
                    },
                    generateSummary: (article: IArticle) => {
                        const profile = superdesk.entities.contentProfile.get(article.profile);
                        const maxCharacterLength = profile.schema['body_html']?.maxlength;

                        return superdesk.httpRequestJsonLocal<{response: string}>({
                            method: 'POST',
                            path: '/belga/ai/toolkit/summarize',
                            payload: {
                                text: article.body_html,
                                maxCharacters: maxCharacterLength != null
                                ? (maxCharacterLength - MAX_CHARACTER_OFFSET)
                                : 0,
                            }
                        }).then((result) => result.response);
                    },
                }));

                return widget;
            }),
        },
        {
            id: 'availability-manager',
            load: () => import('superdesk-core/scripts/extensions/availability-manager').then((extension) => {
                extension.configure({
                    dashboard: {
                        addLinkToSideMenu: {
                            icon: 'user',
                            order: 1100,
                            keyBinding: 'ctrl+alt+c',
                        },

                        tags: {
                            leafsOnly: true,
                        },
                    },
                });

                return extension;
            }),
        },
    ], {
        UserAvatar,
    });
});

export default angular.module('belga', [
    belgaImage.name,
    belga360Archive.name,
    belgaPress.name,
]);
