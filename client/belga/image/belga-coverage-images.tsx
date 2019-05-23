import React from 'react';

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

export default class BelgaCoverage extends React.Component<IProps, IState> {

    readonly state = {loading: false, images: [] as IBelgaImage[]};

    componentDidMount() {
        this.fetchImages();
    }

    componentDidUpdate(prevProps) {
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
                <p className="warn">{'Coverage is empty.'}</p>
            );
        }

        const className = this.props.rendition === 'thumbnail' ?
            'flex-grid flex-grid--boxed flex-grid--wrap-items flex-grid--small-3' :
            'flex-grid flex-grid--boxed flex-grid--wrap-items flex-grid--small-1';

        return (
            <div className={className}>
                {this.state.images.map((image) => (
                    <div key={image.imageId} className="flex-grid__item">
                        <img src={image[this.props.rendition + 'Url']} alt={image.name} />
                    </div>
                ))}
            </div>
        );
    }

}