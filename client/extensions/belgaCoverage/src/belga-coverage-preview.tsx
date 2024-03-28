import * as React from 'react';
import {IPreviewComponentProps, ISuperdesk} from 'superdesk-api';

import {parseIds} from './belga-coverage-editor';
import BelgaCoverageImages from './belga-coverage-images';
import BelgaCoverageCarousel from './belga-coverage-carousel';

export function getBelgaCoveragePreview(superdesk: ISuperdesk) {
    class BelgaCoveragePreview extends React.PureComponent<IPreviewComponentProps<string, {}>> {
        render() {
            const ids = parseIds(this.props.value);

            return (
                <React.Fragment>
                    {ids.map((id) => (
                        <div key={id}>
                            {this.props.item.type !== 'graphic' ? ( // belga coverage in an article
                                <BelgaCoverageCarousel coverageId={id} superdesk={superdesk} preview={true} />
                            ) : ( // single belga coverage in the search, there is description already
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

    return BelgaCoveragePreview;
}
