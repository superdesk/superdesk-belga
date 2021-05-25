import * as React from 'react';
import {IPreviewComponentProps, ISuperdesk} from 'superdesk-api';

import {parseIds} from './belga-coverage-editor';
import BelgaCoverageImages from './belga-coverage-images';
import BelgaCoverageCarousel from './belga-coverage-carousel';

export function getBelgaCoveragePreview(superdesk: ISuperdesk): React.StatelessComponent<IPreviewComponentProps> {
    return function BelgaCoveragePreview(props: IPreviewComponentProps) {
        const ids = parseIds(props.value);

        return (
            <React.Fragment>
                {ids.map((id) => (
                    <div key={id}>
                        {props.item.type !== 'graphic' && (
                            <BelgaCoverageCarousel coverageId={id} superdesk={superdesk} preview={true} />
                        )}
                        {props.item.type === 'graphic' && (
                            <BelgaCoverageImages
                                coverageId={id}
                                rendition={'preview'}
                                maxImages={10}
                                superdesk={superdesk}
                            />
                        )}
                    </div>
                ))}
            </React.Fragment>
        );
    }
}
