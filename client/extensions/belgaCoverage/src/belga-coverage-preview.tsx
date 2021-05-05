import * as React from 'react';
import {IPreviewComponentProps, ISuperdesk} from 'superdesk-api';

import {parseIds} from './belga-coverage-editor';
import BelgaCoverageInfo from './belga-coverage-info';
import BelgaCoverageImages from './belga-coverage-images';

export function getBelgaCoveragePreview(superdesk: ISuperdesk): React.StatelessComponent<IPreviewComponentProps> {
    return function BelgaCoveragePreview(props: IPreviewComponentProps) {
        const ids = parseIds(props.value);

        console.info('ids', ids, props.value);

        return (
            <React.Fragment>
                {ids.map((id) => (
                    <div key={id}>
                        {props.item.type !== 'graphic' &&
                            <BelgaCoverageInfo coverageId={id} superdesk={superdesk} />
                        }
                        <BelgaCoverageImages
                            coverageId={id}
                            rendition={'preview'}
                            maxImages={10}
                            superdesk={superdesk}
                        />
                    </div>
                ))}
            </React.Fragment>
        );
    }
}
