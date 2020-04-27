import React from 'react';
import angular from 'angular';
import {IUser} from 'superdesk-api';
import {startApp} from 'superdesk-core/scripts/index';
import belgaImage from './image';
import belga360Archive from './360archive';
import markForUserExtension from 'superdesk-core/scripts/extensions/markForUser/dist/src/extension';
import datetimeFieldExtension from 'superdesk-core/scripts/extensions/datetimeField/dist/src/extension';
import belgaCoverageExtension from '../extensions/belgaCoverage/dist/index';
import updateArticleOnProfileChangeExtension from '../extensions/updateArticleOnProfileChange/dist/src/extension';
import iptcExtension from '../extensions/iptc/dist/extension'
import {AvatarContentText} from 'superdesk-ui-framework';
import planningExtension from 'superdesk-planning/client/planning-extension/dist/extension';

class UserAvatar extends React.PureComponent<{user: IUser}> {
    render() {
        return (
            <AvatarContentText
                text={this.props.user.sign_off}
                tooltipText={this.props.user.display_name}
            />
        );
    }
}

setTimeout(() => {
    startApp([
        planningExtension,
        markForUserExtension,
        datetimeFieldExtension,
        belgaCoverageExtension,
        updateArticleOnProfileChangeExtension,
        iptcExtension,
    ],{UserAvatar});
});

export default angular.module('belga', [
    belgaImage.name,
    belga360Archive.name,
]);
