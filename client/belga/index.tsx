import React from 'react';
import angular from 'angular';
import {IUser} from 'superdesk-api'
import {startApp} from 'superdesk-core/scripts/index';
import belgaImage from './image';
import belga360Archive from './360archive';
import planningExtension from '../node_modules/superdesk-planning/client/planning-extension/dist/src/extension';
import markForUserExtension from '../node_modules/superdesk-core/scripts/extensions/markForUser/dist/src/extension';
import belgaCoverageExtension from '../extensions/belgaCoverage/dist/index';

class UserAvatar extends React.Component<{user: IUser}> {
    render() {
        return (
            <div className="user-avatar" data-test-id="user-avatar">
                <figure className="avatar avatar--no-margin initials">
                    {this.props.user.sign_off}
                </figure>
            </div>
        );
    }
}

setTimeout(() => {
    startApp([
        planningExtension,
        markForUserExtension,
        belgaCoverageExtension,
    ],{UserAvatar});
});

export default angular.module('belga', [
    belgaImage.name,
    belga360Archive.name,
]);
