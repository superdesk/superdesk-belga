import React from 'react';
import angular from 'angular';
import {IUser} from 'superdesk-api'
import {startApp} from 'superdesk-core/scripts/index';
import belgaImage from './image';

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
    startApp({UserAvatar});
});

export default angular.module('belga', [
    belgaImage.name,
]);
