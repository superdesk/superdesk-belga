import * as React from 'react';
import angular from 'angular';

import {IUser} from 'superdesk-api';
import {startApp} from 'superdesk-core/scripts/index';
import {AvatarContentText} from 'superdesk-ui-framework';

import belgaImage from './belga/image';
import belga360Archive from './belga/360archive';
import belgaPress from './belga/belgapress';

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
    ], {
        UserAvatar,
    });
});

export default angular.module('belga', [
    belgaImage.name,
    belga360Archive.name,
    belgaPress.name,
]);
