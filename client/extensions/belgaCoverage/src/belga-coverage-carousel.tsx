import * as React from 'react';

import {ISuperdesk} from 'superdesk-api';
import {Badge, Carousel, IconButton} from 'superdesk-ui-framework';
import {IBelgaCoverage, getCoverageInfo, getCoverageImages, IBelgaImage} from './belga-image-api';
import 'superdesk-ui-framework/dist/superdesk-ui.bundle.css';

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
        const {formatDate} = this.props.superdesk.localization;

        if (this.state.coverage == null || this.state.images == null) {
            return (
                <Alert type="error">{'There was an error when fetching coverage ' + this.props.coverageId}</Alert>
            );
        }

        const {preview} = this.props;
        const {coverage, images} = this.state;


        const itemTemplate = (props: IBelgaImage) => (
            <div className="sd-thumb-carousel__item">
                <div className="sd-thumb-carousel__item-inner">
                    <img src={props.thumbnailUrl} alt={props.name} />
                </div>
            </div>
        );

        const headerTemplate = (
            <div className="sd-thumb-carousel__header">
                <h4 className="sd-thumb-carousel__heading">{coverage.name}</h4>
                <Badge text={'' + coverage.nrImages} type='light' />
                {preview !== true && (
                    <div className="sd-thumb-carousel__header-block--r">
                        <time>{formatDate(coverage.createDate)}</time>
                        {this.props.removeCoverage != null && (
                            <IconButton icon="trash" ariaValue="Remove" onClick={() => this.props.removeCoverage ? this.props.removeCoverage() : null} />
                        )}
                    </div>
                )}
            </div>
        );

        const footerTemplate = (
            <div className="sd-thumb-carousel__description">
                {coverage.description}
            </div>
        );

        const numImages = preview === true ? 1 : 3;

        return (
            <Carousel
                items={images}
                itemTemplate={itemTemplate}
                headerTemplate={headerTemplate}
                footerTemplate={footerTemplate}
                numVisible={numImages}
                numScroll={numImages}
            />
        );
    }
}