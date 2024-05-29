
document.addEventListener('htmx:afterSwap', function () {
    window.scrollTo(0, 0);
    playlistController.loadSongIntoPlaylist();
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function inc_view_count(songName) {
    var xhr = new XMLHttpRequest();
    var domain = window.location.host;
    var csrftoken = getCookie('csrftoken');
    xhr.open('POST', 'http://' + domain + '/song/inc_view_count/', true);
    xhr.setRequestHeader("X-CSRFToken", csrftoken);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send(JSON.stringify({song_name: songName}));
}

document.querySelectorAll('.play-button').forEach(function (button) {
    button.addEventListener('click', function () {
        var songUrl = button.getAttribute('data-url');
        var songImage = button.getAttribute('data-image');
        var songArtist = button.getAttribute('data-artist');
        var songName = button.getAttribute('data-name');
        var songId = button.getAttribute('data-id');
        musicPlayer.playSong(songUrl, songImage, songArtist, songName, songId);
    });
});

document.querySelectorAll('.add-button').forEach(function (button) {
    button.addEventListener('click', function () {
        var songUrl = button.getAttribute('data-url');
        var songImage = button.getAttribute('data-image');
        var songArtist = button.getAttribute('data-artist');
        var songName = button.getAttribute('data-name');
        var songId = button.getAttribute('data-id');
        musicPlayer.addToPlaylist(songUrl, songImage, songArtist, songName, songId);
    });
});

document.querySelectorAll('.add-all-button').forEach(function (button) {
    button.addEventListener('click', function () {
        var albumInfo = button.getAttribute('data-album');
        var songInfoArray = JSON.parse(albumInfo);

        songInfoArray.forEach(function (songInfo) {
            var songUrl = songInfo.stream_url;
            var songImage = songInfo.image_uri;
            var songArtist = songInfo.artist_name;
            var songName = songInfo.song_name;
            var songId = songInfo.id;

            musicPlayer.addToPlaylist(songUrl, songImage, songArtist, songName, songId);
        });
    });
});


document.querySelectorAll('.play-all-button').forEach(function (button) {
    button.addEventListener('click', function () {
        var albumInfo = button.getAttribute('data-album');
        var songInfoArray = JSON.parse(albumInfo);
        musicPlayer.clearPlaylist();
        musicPlayer.playSong(songInfoArray[0].stream_url, songInfoArray[0].image_uri, songInfoArray[0].artist_name, songInfoArray[0].song_name, songInfoArray[0].id);
        songInfoArray.forEach(function (songInfo) {
            var songUrl = songInfo.stream_url;
            var songImage = songInfo.image_uri;
            var songArtist = songInfo.artist_name;
            var songName = songInfo.song_name;
            var songId = songInfo.id;

            musicPlayer.addToPlaylist(songUrl, songImage, songArtist, songName, songId);
        });
        playlistController.loadSongIntoPlaylist();
    });
});