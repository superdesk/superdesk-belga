import * as React from 'react';
import {ISuperdesk} from 'superdesk-api';

import {getCoverageImages, IBelgaImage} from './belga-image-api';

interface IProps {
    maxImages: number;
    coverageId: string;
    rendition: 'preview' | 'thumbnail';
    superdesk: ISuperdesk;
}

interface IState {
    loading: boolean;
    images: Array<IBelgaImage>;
}

function getImageUrl(image: IBelgaImage, rendition: IProps['rendition']): string {
    switch (rendition) {
        case 'preview':
            return image.previewUrl;
        case 'thumbnail':
            return image.thumbnailUrl;
    }
}

export default class BelgaCoverage extends React.PureComponent<IProps, IState> {

    constructor(props: IProps) {
        super(props);
        this.state = {loading: false, images: []};
    }

    componentDidMount() {
        this.fetchImages();
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
        const {Alert, Grid} = this.props.superdesk.components;

        if (this.state.loading) {
            return null;
        }

        if (this.state.images.length === 0) {
            return (
                <Alert type="warning" message={'Coverage is empty.'} />
            );
        }

        return (
            <Grid columns={this.props.rendition === 'thumbnail' ? 3 : 1} boxed={true}>
                {this.state.images.map((image) => (
                    <img key={image.imageId} src={getImageUrl(image, this.props.rendition)} alt={image.name} />
                ))}
            </Grid>
        );
    }

}