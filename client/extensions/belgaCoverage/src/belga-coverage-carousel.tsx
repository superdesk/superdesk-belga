import * as React from 'react';

import {ISuperdesk} from 'superdesk-api';
import {Carousel, IconButton} from 'superdesk-ui-framework';
import {IBelgaCoverage, getCoverageInfo, getCoverageImages, IBelgaImage} from './belga-image-api';

interface IProps {
    preview?: boolean;
    coverageId: string;
    removeCoverage?: () => void;
    superdesk: ISuperdesk;
}

interface IState {
    loading: boolean;
    coverage: IBelgaCoverage | null;
    images: Array<IBelgaImage> | null;
}

export default class BelgaCoverageCarousel extends React.PureComponent<IProps, IState> {
    constructor(props: IProps) {
        super(props);

        this.state = {
            loading: true,
            coverage: null,
            images: null,
        };
    }

    componentDidMount() {
        Promise.all([
            getCoverageInfo(this.props.coverageId),
            getCoverageImages(this.props.coverageId, 8),
        ]).then(([coverage, images]) => {
            this.setState({
                loading: false,
                coverage,
                images,
            });
        }).catch((err) => {
            console.error(err);
            this.setState({
                loading: false,
            });
        });
    }

    render() {
        if (this.state.loading) {
            return (
                <div className="sd-loader" />
            );
        }

        const {Alert} = this.props.superdesk.components;
        const {gettext, formatDate} = this.props.superdesk.localization;

        if (this.state.coverage == null || this.state.images == null) {
            return (
                <Alert type="error" message={`There was an error when fetching coverage ${this.props.coverageId}`} />
            );
        }

        const {preview} = this.props;
        const {coverage, images} = this.state;

        const headerMeta = preview !== true ? (
            <React.Fragment>
                <time>{formatDate(coverage.createDate)}</time>
                {this.props.removeCoverage != null && (
                    <IconButton icon="trash" ariaValue={gettext("Remove")} onClick={() => this.props.removeCoverage ? this.props.removeCoverage() : null} />
                )}
            </React.Fragment>
        ) : undefined;

        const numImages = preview === true ? 1 : 3;

        return (
            <Carousel
                images={images.map((image) => ({
                    src: image.thumbnailUrl,
                    alt: image.name,
                }))}
                numVisible={numImages}
                numScroll={numImages}
                title={coverage.name}
                imageCount={coverage.nrImages}
                description={coverage.description}
                headerMeta={headerMeta}
            />
        );
    }
}
