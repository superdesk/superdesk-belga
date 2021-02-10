import React from 'react';
import angular from 'angular';
import {IUser} from 'superdesk-api';
import {startApp} from 'superdesk-core/scripts/index';
import belgaImage from './image';
import belga360Archive from './360archive';
import belgaPress from './belgapress';
import {AvatarContentText} from 'superdesk-ui-framework';


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
        {id: 'planning-extension', load: () => import('superdesk-planning/client/planning-extension/dist/extension').then((res) => res.default)},
        {id: 'markForUser', load: () => import('superdesk-core/scripts/extensions/markForUser/dist/src/extension').then((res) => res.default)},
        {id: 'datetimeField', load: () => import('superdesk-core/scripts/extensions/datetimeField/dist/src/extension').then((res) => res.default)},
        {id: 'belgaCoverage', load: () => import('../extensions/belgaCoverage/dist/index').then((res) => res.default)},
        {id: 'updateArticleOnProfileChange', load: () => import('../extensions/updateArticleOnProfileChange/dist/src/extension').then((res) => res.default)},
        {id: 'saveArticleOnComingUpChange', load: () => import('../extensions/saveArticleOnComingUpChange/dist/src/extension').then((res) => res.default)},
        {id: 'iptc', load: () => import('../extensions/iptc/dist/extension').then((res) => res.default)},
    ], {UserAvatar});
});

export default angular.module('belga', [
    belgaImage.name,
    belga360Archive.name,
    belgaPress.name,
]);
