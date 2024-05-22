
var MusicPlayer = MusicPlayer || (function() {
    var instance;

    function createInstance() {

        let audioElement = new Audio();
        audioElement.volume = 1;
        var playPauseButton = document.querySelector('.play-pause');
        var playlist = [];
        var currentSongIndex = 0;
        var nextButton = document.querySelector('.fa-step-forward');
        var prevButton = document.querySelector('.fa-step-backward');
        var repeatButton = document.querySelector('.fa-undo-alt');
        var progressBar = document.querySelector('.progress-bar');
        var progress = document.querySelector('.progress');
        progress.style.width = '0%';
        var isDraggingProgress = false;
        var isPlaying = false;
        var currentTimeElement = document.querySelector('.progress-container span:first-child');
        var durationTimeElement = document.querySelector('.progress-container span:last-child');
        var volumeBar = document.querySelector('.volume-bar .progress-bar');
        var volumeProgress = document.querySelector('.volume-bar .progress');
        volumeProgress.style.width = '100%';
        var isDragging = false;
        var volumeButton = document.querySelector('.fas.fa-volume-up');
        var isMuted = false;
        var previousVolume = audioElement.volume;


        audioElement.addEventListener('ended', function() {
        var song;
        var index = -1;
        var end_playlist = false;

        for (var i = 0; i < playlist.length; i++) {
            if (new URL(playlist[i].url, window.location.origin).href === audioElement.src) {
                index = i;
                break;
            }
        }

        if (index !== -1) {
            currentSongIndex = index + 1;

            if (currentSongIndex >= playlist.length) {
                currentSongIndex = 0;
                end_playlist = true;
            }
        } else if (playlist.length > 0) {
            currentSongIndex = 0;
        } else {
            return;
        }

        song = playlist[currentSongIndex];

        audioElement.src = song.url;

        document.querySelector('.image-container img').src = song.image;
        document.querySelector('.song-description .title').textContent = song.name;
        document.querySelector('.song-description .artist').textContent = song.artist;
        playPauseButton.classList.remove('play');
        playPauseButton.classList.add('pause');
        progress.style.width = '0%';
        if (!end_playlist) {
            audioElement.play();
        }
        loadSongIntoPlaylist();
    });
        audioElement.addEventListener('play', function() {
            playPauseButton.classList.remove('pause');
            playPauseButton.classList.add('play');
        });
        audioElement.addEventListener('pause', function() {
            playPauseButton.classList.remove('play');
            playPauseButton.classList.add('pause');
        });
        playPauseButton.addEventListener('click', function() {
            if (audioElement.src !== '') {
                if (audioElement.paused) {
                    audioElement.play();
                } else {
                    audioElement.pause();
                }
            }
        });

        function playSong(songUrl, songImage, songArtist, songName) {
            document.querySelector('.image-container img').src = songImage;
            document.querySelector('.song-description .title').textContent = songName;
            document.querySelector('.song-description .artist').textContent = songArtist;


            if (songUrl !== '') {
                audioElement.src = songUrl;
                audioElement.play();
            }
            loadSongIntoPlaylist();
        }

        function addToPlaylist(songUrl, songImage, songArtist, songName) {
            for (var i = 0; i < playlist.length; i++) {
                if (playlist[i].url === songUrl) {
                    return;
                }
            }

            playlist.push({
                url: songUrl,
                image: songImage,
                artist: songArtist,
                name: songName
            });
            if (audioElement.ended || !audioElement.src) {
                playSong(songUrl, songImage, songArtist, songName);
            }
            loadSongIntoPlaylist();
        }
        function clearPlaylist() {
            playlist.length = 0;
        }

        nextButton.addEventListener('click', function() {
            var index= -1;
            for (var i = 0; i < playlist.length; i++) {
                if (new URL(playlist[i].url, window.location.origin).href === audioElement.src) {
                    index = i;
                    break;
                }
            }

            currentSongIndex = index + 1;

            if (currentSongIndex >= playlist.length) {
                currentSongIndex = 0;
            }
            if (playlist.length > 0) {
                var song = playlist[currentSongIndex];
                playSong(song.url, song.image, song.artist, song.name);
            }
        });

        prevButton.addEventListener('click', function() {
            var index= 1;
            for (var i = 0; i < playlist.length; i++) {
                if (new URL(playlist[i].url, window.location.origin).href === audioElement.src) {
                    index = i;
                    break;
                }
            }
            currentSongIndex = index - 1;

            if (currentSongIndex < 0) {
                currentSongIndex = playlist.length - 1;
            }
            if (playlist.length > 0) {
                var song = playlist[currentSongIndex];
                playSong(song.url, song.image, song.artist, song.name);
            }
        });

        repeatButton.addEventListener('click', function() {
            if (audioElement.loop) {
                audioElement.loop = false;
                repeatButton.style.color = '#fff';
            } else {
                audioElement.loop = true;
                repeatButton.style.color = '#f00';
                if (audioElement.currentTime === audioElement.duration) {
                    audioElement.currentTime = 0;
                    audioElement.play();
                    playPauseButton.classList.remove('pause');
                    playPauseButton.classList.add('play');
                }
            }
        });

        audioElement.addEventListener('timeupdate', function() {
            var progressBar = document.querySelector('.progress');
            var progress = (audioElement.currentTime / audioElement.duration) * 100;
            progressBar.style.width = progress + '%';
        });

        progressBar.addEventListener('mousedown', function(e) {
            isDraggingProgress = true;
            isPlaying = !audioElement.paused;
            audioElement.pause();
            updateProgress(e);
        });

        window.addEventListener('mousemove', function(e) {
            if (isDraggingProgress) {
                updateProgress(e);
            }
        });

        window.addEventListener('mouseup', function(e) {
            if (isDraggingProgress) {
                isDraggingProgress = false;
                updateProgress(e);
                if (isPlaying) {
                    audioElement.play();
                }
            }
        });

        function updateProgress(e) {
            var rect = progressBar.getBoundingClientRect();
            var x = e.clientX - rect.left;
            var width = rect.right - rect.left;
            var progressValue = x / width;
            progressValue = Math.min(Math.max(progressValue, 0), 1); // Ensure progressValue is between 0 and 1
            audioElement.currentTime = progressValue * audioElement.duration;
            progress.style.width = (progressValue * 100) + '%';
        }

        audioElement.addEventListener('loadedmetadata', function() {
            var durationMinutes = Math.floor(audioElement.duration / 60);
            var durationSeconds = Math.floor(audioElement.duration % 60);
            if (durationSeconds < 10) durationSeconds = '0' + durationSeconds;
            durationTimeElement.textContent = durationMinutes + ':' + durationSeconds;
        });

        audioElement.addEventListener('timeupdate', function() {
            var currentMinutes = Math.floor(audioElement.currentTime / 60);
            var currentSeconds = Math.floor(audioElement.currentTime % 60);
            if (currentSeconds < 10) currentSeconds = '0' + currentSeconds;
            currentTimeElement.textContent = currentMinutes + ':' + currentSeconds;
        });
        audioElement.addEventListener('volumechange', function() {
            var volume = audioElement.volume;

            if (volume > 0.5) {
                volumeButton.className = 'fas fa-volume-up';
            } else if (volume !== 0) {
                volumeButton.className = 'fas fa-volume-down';
            } else {
                volumeButton.className = 'fas fa-volume-mute';
            }
        });
        volumeBar.addEventListener('mousedown', function(e) {
            isDragging = true;
            updateVolume(e);
        });

        window.addEventListener('mousemove', function(e) {
            if (isDragging) {
                updateVolume(e);
            }
        });

        window.addEventListener('mouseup', function(e) {
            if (isDragging) {
                isDragging = false;
                updateVolume(e);
            }
        });

        function updateVolume(e) {
            var rect = volumeBar.getBoundingClientRect();
            var x = e.clientX - rect.left;
            var width = rect.right - rect.left;
            var volume = x / width;
            volume = Math.min(Math.max(volume, 0), 1);
            audioElement.volume = volume;
            volumeProgress.style.width = (volume * 100) + '%';
        }

        volumeButton.addEventListener('click', function() {
            if (isMuted) {

                audioElement.volume = previousVolume;
                volumeProgress.style.width = (previousVolume * 100) + '%';
                volumeButton.classList.remove('fa-volume-mute');
                volumeButton.classList.add('fa-volume-down');
                isMuted = false;
            } else if (audioElement.volume > 0) {

                previousVolume = audioElement.volume;
                audioElement.volume = 0;
                volumeProgress.style.width = '0%';
                volumeButton.classList.remove('fa-volume-down');
                volumeButton.classList.add('fa-volume-mute');
                isMuted = true;
            }
        });

        return {
            playSong: playSong,
            addToPlaylist: addToPlaylist,
            playlist: playlist,
            audioElement: audioElement,
            clearPlaylist: clearPlaylist,
        };
    }

    return {
        getInstance: function() {
            if (!instance) {
                instance = createInstance();
            }
            return instance;
        }
    };
})();

var musicPlayer = MusicPlayer.getInstance();

