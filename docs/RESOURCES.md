Each _sites/*/resources folder is a home for any files that need to be created in the corresponding _docker-compose.yml_ OUTSIDE the site's Drupal webroot (/var/www/html/web).

Common elements include:  

_.bashrc_ - Deployed to the _wodby_ user's home to establish new command aliases
_fix-permissions.sh_ - Deployed to _wodby_'s .composer/vendor/bin (in _wodby_'s path) as _fix-permissions_

Drupal 7 examples include:  

  _admin.aliases.drushrc.php_ - Defines Drush aliases for `admin` in the _wodby_ user's _~/.drush_ directory
  _crb.aliases.drushrc.php_ - Defines Drush aliases for `crb` in the _wodby_ user's _~/.drush_ directory
  _htlt.aliases.drushrc.php_ - Defines Drush aliases for `htlt` in the _wodby_ user's _~/.drush_ directory
  _stcrec.aliases.drushrc.php_ - Defines Drush aliases for `stcrec` in the _wodby_ user's _~/.drush_ directory
  _.bashrc_ - Deployed to the _wodby_ user's home to establish new command aliases
