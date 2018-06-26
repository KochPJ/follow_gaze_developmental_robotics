% Demo script to use the gaze following model
% Written by Adria Recasens (recasens@mit.edu)

function line = folow_gaze(x, y)
    % add / change this to your caffe path
    addpath(genpath('/home/tjalling/Desktop/ru/DevRob/caffe/matlab/'));
    addpath(genpath('/home/paul/programs/caffe/matlab/'));

    im = imread('currentView.png');

    % Get the coordinate of the eye, and recalc to ratio of image x / y
    x = double(x);
    y = double(y);
    xWidth = size(im,2);
    yWidth = size(im,1);
    e = [x/xWidth y/yWidth]


    % Compute Gaze
    [x_predict,y_predict,heatmap,net] = predict_gaze(im,e);

    %Visualization
    g = floor([x_predict y_predict].*[size(im,2) size(im,1)]);
    e = floor(e.*[size(im,2) size(im,1)]);
    line = [e(1) e(2) g(1) g(2)];
    im = insertShape(im,'line',line,'Color','red','LineWidth',8);

    image(im);
end
