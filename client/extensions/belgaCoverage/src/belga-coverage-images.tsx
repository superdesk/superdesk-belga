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
        const {components} = this.props.superdesk;

        if (this.state.loading) {
            return null;
        }

        if (this.state.images.length === 0) {
            return (
                <components.Alert type="warning">{'Coverage is empty.'}</components.Alert>
            );
        }

        return (
            <components.Grid columns={this.props.rendition === 'thumbnail' ? 3 : 1} boxed={true}>
                {this.state.images.map((image) => (
                    <img key={image.imageId} src={getImageUrl(image, this.props.rendition)} alt={image.name} />
                ))}
            </components.Grid>
        );
    }

}