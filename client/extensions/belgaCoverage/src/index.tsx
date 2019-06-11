import * as React from 'react';
import {ISuperdesk, IExtension, IExtensionActivationResult, IEditorComponentProps, IPreviewComponentProps} from 'superdesk-api';

import {BelgaCoverageEditor} from './belga-coverage-editor';
import {BelgaCoveragePreview} from './belga-coverage-preview';

const extension: IExtension = {
    activate: (superdesk: ISuperdesk) => {
        const result: IExtensionActivationResult = {
            contributions: {
                customFieldTypes: [
                    {
                        id: 'belga.coverage',
                        label: superdesk.localization.gettext('Belga Coverage'),
                        editorComponent: (props: IEditorComponentProps) => (
                            <BelgaCoverageEditor {...props} superdesk={superdesk} />
                        ),
                        previewComponent: (props: IPreviewComponentProps) => (
                            <BelgaCoveragePreview {...props} superdesk={superdesk} />
                        ),
                    }
                ]
            }

        };

        return Promise.resolve(result);
    },
};

export default extension;
