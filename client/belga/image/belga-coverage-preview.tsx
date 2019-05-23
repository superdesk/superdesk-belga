import React from 'react';

import {IPreviewComponentProps} from 'superdesk-core/scripts/apps/fields';

import BelgaCoverageInfo from './belga-coverage-info';
import BelgaCoverageImages from './belga-coverage-images';

export default function BelgaCoveragePreview(props: IPreviewComponentProps) {
    return (
        <div>
            {props.item.type !== 'graphic' &&
                <BelgaCoverageInfo coverageId={props.value} />
            }
            <BelgaCoverageImages
                coverageId={props.value}
                rendition={'preview'}
                maxImages={10}
            />
        </div>
    );
}