import {ISuperdesk, IExtension, IExtensionActivationResult} from 'superdesk-api';

import {getBelgaCoverageEditor} from './belga-coverage-editor';
import {getBelgaCoveragePreview} from './belga-coverage-preview';

const extension: IExtension = {
    activate: (superdesk: ISuperdesk) => {
        const gettext = superdesk.localization.gettext;
        const result: IExtensionActivationResult = {
            contributions: {
                customFieldTypes: [
                    {
                        id: 'belga.coverage',
                        label: gettext('Belga Coverage'),
                        editorComponent: getBelgaCoverageEditor(superdesk),
                        previewComponent: getBelgaCoveragePreview(superdesk),
                    }
                ]
            }

        };

        return Promise.resolve(result);
    },
};

export default extension;
