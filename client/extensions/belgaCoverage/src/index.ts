import {ISuperdesk, IExtension, IExtensionActivationResult, ICustomFieldType, ICommonFieldConfig} from 'superdesk-api';

import {getBelgaCoverageEditor} from './belga-coverage-editor';
import {getBelgaCoveragePreview} from './belga-coverage-preview';

const extension: IExtension = {
    activate: (superdesk: ISuperdesk) => {
        const gettext = superdesk.localization.gettext;
        const field: ICustomFieldType<string, string, ICommonFieldConfig, never> = {
            id: 'belga.coverage',
            label: gettext('Belga Coverage'),
            editorComponent: getBelgaCoverageEditor(superdesk),
            previewComponent: getBelgaCoveragePreview(superdesk),
            hasValue: (value) => value != null && value.length > 0,
            getEmptyValue: () => '',
            generic: true,
        };

        const result: IExtensionActivationResult = {
            contributions: {
                customFieldTypes: [field],
            },
        };

        return Promise.resolve(result);
    },
};

export default extension;
