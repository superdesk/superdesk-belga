import * as React from 'react';
import {ICustomFieldType, IPreviewComponentProps} from 'superdesk-api';

import BelgaCoverageInfo from './belga-coverage-info';
import BelgaCoverageImages from './belga-coverage-images';

export const BelgaCoveragePreview: ICustomFieldType['previewComponent'] = (props: IPreviewComponentProps) => {
    return (
        <div>
            {props.item.type !== 'graphic' &&
                <BelgaCoverageInfo coverageId={props.value} superdesk={props.superdesk} />
            }
            <BelgaCoverageImages
                coverageId={props.value}
                rendition={'preview'}
                maxImages={10}
                superdesk={props.superdesk}
            />
        </div>
    );
}