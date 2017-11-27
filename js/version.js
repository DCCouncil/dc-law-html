$(document).ready(function() {
  function renderMustacheData(data) {
    $('title, body').each(function(_, el) {
      var template = $(el).html();
      var rendered = Mustache.render(template, data);
      $(el).html(rendered);
    });
  }

  function getLatestMaster(repo) {
    return $.get('https://api.github.com/repos/' + repo + '/commits/master');
  }

  function getLatestRelease(repo) {
    return $.get('https://api.github.com/repos/' + repo + '/releases/latest').then(function(data) {
      return $.get('https://api.github.com/repos/' + repo + '/commits/' + data.tag_name);
    });
  }

  function triggerGitHubCalls() {
    var host = window.location.hostname.split('.')[0];
    var gitHubCall = (host === 'development') ? getLatestMaster : getLatestRelease;

    $('[data-repo]').each(function(_, el) {
      var repo = $(el).data('repo');

      gitHubCall(repo).then(function(data) {
        var headSha = data.sha;
        var thisSha = $(el).text();

        if (headSha === thisSha) {
          $(el).addClass('success');
        } else {
          $(el).addClass('error');
          var tooltip = [
            'Latest: ' + headSha,
            'Date: ' + data.commit.committer.date,
            'Message: ' + data.commit.message
          ].join('\n')
          $(el).prop('title', tooltip);
        }
      });
    });
  }

  $.get($('body').data('url'), renderMustacheData, 'json').then(triggerGitHubCalls);
});
