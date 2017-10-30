var gulp = require('gulp');
var sass = require('gulp-sass');
var connect = require('gulp-connect');
var inject = require('gulp-inject');
var series = require('stream-series');
var uglify = require('gulp-uglify');
var concat = require('gulp-concat');

/** browserify
 var browserify = require('browserify');
 var source = require('vinyl-source-stream');
 */

var bowerFiles = require('main-bower-files');

gulp.task('connect', function () {
    connect.server({
        root: '',
        port: 4014
    });
});

gulp.task('styles', function () {
    gulp.src('./app/styles/*.scss')
            .pipe(sass().on('error', sass.logError))
            .pipe(gulp.dest('./app/styles/'))
});

gulp.task('index', function () {
    var target = gulp.src('./app/index.html');
    var sources = gulp.src(['./app/**/*.js', './app/**/*.css'], {
        read: false
    });
    var bowerSources = gulp.src(bowerFiles(), {
        read: false
    });

    var othersBowerSources = gulp.src(["bower_components/angular/angular.min.js", "bower_components/material-angular-paging/build/dist.min.js"]);

    return target
            .pipe(inject(series(othersBowerSources, sources),{
                addRootSlash: false
            }))
            .pipe(inject(bowerSources, {
                name: 'bower',
                addRootSlash: false
            }, {
                relative: true
            }))
            .pipe(gulp.dest(''));
});

gulp.task('minify', function () {
    gulp.src(['app/**/*.js'])
            .pipe(concat('all.js'))
            .pipe(uglify())
            .pipe(gulp.dest(''));
});

gulp.task('watch', function () {
    gulp.watch('app/**/*.js', ['index']);
    gulp.watch('app/**/*.html', ['index']);
    gulp.watch('app//styles/**/*.scss', ['styles']);
});

gulp.task('browserify', function () {
});

gulp.task('default', ['styles', 'index', 'connect', 'watch']);

gulp.task('release', ['styles', 'index', 'minify']);
