var PlaylistController = (function () {
    var instance;

    function createInstance() {
        document.querySelector('.playlist-box');

        var playlistBox = document.querySelector('.playlist-box .songs');

        playlistBox.addEventListener('wheel', function(e) {
            var atTop = playlistBox.scrollTop === 0;
            var atBottom = playlistBox.scrollHeight - playlistBox.scrollTop === playlistBox.clientHeight;

            var delta = e.deltaY;

            if ((delta < 0 && atTop) || (delta > 0 && atBottom)) {
                e.preventDefault();
            } else {
                e.stopPropagation();
            }
        }, { passive: false });


        return {

            loadSongIntoPlaylist: function () {
                var playlist = document.getElementById('playlist');
                var MPplaylist = musicPlayer.playlist;

                playlist.innerHTML = '';

                for (var i = 0; i < MPplaylist.length; i++) {
                    var song = MPplaylist[i];
                    var a = document.createElement('a');
                    a.href = '/song/' + song.id + "/info/"
                    a.setAttribute('hx-get', '/song/' + song.id + "/info/");
                    a.setAttribute('hx-target', '#swap');
                    a.setAttribute('hx-swap', 'outerHTML');
                    a.textContent = song.name;

                    playlist.appendChild(a);
                    if (musicPlayer.audioElement.src.includes(song.url)) {
                        a.classList.add('playing');
                    }
                }
                htmx.process(playlist);
            }
        };
    }

    return {
        getInstance: function () {
            if (!instance) {
                instance = createInstance();
            }
            return instance;
        }
    };
})();

var playlistController = PlaylistController.getInstance();