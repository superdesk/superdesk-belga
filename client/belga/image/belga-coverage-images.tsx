import React from 'react';

import {Grid} from 'superdesk-core/scripts/core/ui/components/grid';
import {Alert} from 'superdesk-core/scripts/core/ui/components/alert';

import {getCoverageImages, IBelgaImage} from './belga-image-api';

interface IProps {
    maxImages: number;
    coverageId: string;
    rendition: 'preview' | 'thumbnail';
}

interface IState {
    loading: boolean;
    images: Array<IBelgaImage>;
}

const URLS = {
    preview: 'previewUrl',
    thumbnail: 'thumbnailUrl',
};

export default class BelgaCoverage extends React.Component<IProps, IState> {

    readonly state = {loading: false, images: [] as IBelgaImage[]};

    componentDidMount() {
        this.fetchImages();
    }

    componentDidUpdate(prevProps: IProps) {
        if (prevProps.coverageId !== this.props.coverageId) {
            this.fetchImages();
        }
    }

    fetchImages() {
        this.setState({loading: true});

        getCoverageImages(this.props.coverageId, this.props.maxImages)
            .then((images) => this.setState({loading: false, images: images}))
            .catch(() => {
                this.setState({loading: false});
            });
    }

    render() {
        if (this.state.loading) {
            return null;
        }

        if (this.state.images.length === 0) {
            return (
                <Alert type="warning">{'Coverage is empty.'}</Alert>
            );
        }

        return (
            <Grid columns={this.props.rendition === 'thumbnail' ? 3 : 1} boxed={true}>
                {this.state.images.map((image) => (
                    <img key={image.imageId} src={image[URLS[this.props.rendition]]} alt={image.name} />
                ))}
            </Grid>
        );
    }

}