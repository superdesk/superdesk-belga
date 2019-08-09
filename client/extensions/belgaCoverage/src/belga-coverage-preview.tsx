import * as React from 'react';
import {IPreviewComponentProps, ISuperdesk} from 'superdesk-api';

import BelgaCoverageInfo from './belga-coverage-info';
import BelgaCoverageImages from './belga-coverage-images';

export function getBelgaCoveragePreview(superdesk: ISuperdesk): React.StatelessComponent<IPreviewComponentProps> {
    return function BelgaCoveragePreview(props: IPreviewComponentProps) {
        return (
            <div>
                {props.item.type !== 'graphic' &&
                    <BelgaCoverageInfo key={props.value} coverageId={props.value} superdesk={superdesk} />
                }
                <BelgaCoverageImages
                    key={props.value}
                    coverageId={props.value}
                    rendition={'preview'}
                    maxImages={10}
                    superdesk={superdesk}
                />
            </div>
        );
    }
}
