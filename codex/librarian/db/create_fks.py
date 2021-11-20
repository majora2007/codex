"""
Create all missing comic foreign keys for an import.

So we may safely create the comics next.
"""

from logging import getLogger
from pathlib import Path

from django.db.models.functions import Now

from codex.models import (
    Credit,
    CreditPerson,
    CreditRole,
    Folder,
    Imprint,
    Publisher,
    Series,
    Volume,
)


BULK_UPDATE_FOLDER_MODIFIED_FIELDS = ("stat", "updated_at")
LOG = getLogger(__name__)


def _create_group_obj(cls, group_param_tuple, count):
    """Create a set of browser group objects."""
    defaults = {"name": group_param_tuple[-1]}
    if cls in (Imprint, Series, Volume):
        defaults["publisher"] = Publisher.objects.get(name=group_param_tuple[0])
    if cls in (Series, Volume):
        defaults["imprint"] = Imprint.objects.get(
            publisher=defaults["publisher"],
            name=group_param_tuple[1],
        )
    if cls is Series:
        defaults["volume_count"] = count
    if cls is Volume:
        defaults["series"] = Series.objects.get(
            publisher=defaults["publisher"],
            imprint=defaults["imprint"],
            name=group_param_tuple[2],
        )
        defaults["issue_count"] = count

    group_obj = cls(**defaults)
    group_obj.presave()
    return group_obj


def _bulk_create_groups(all_create_groups):
    """Create missing groups breadth first."""
    # TODO special code for updating series and volume counts
    if not all_create_groups:
        return False
    LOG.verbose("Preparing groups for creation...")  # type: ignore

    num_create_groups = 0
    for cls, group_tree_counts in all_create_groups.items():
        if not group_tree_counts:
            continue
        create_groups = []
        for group_param_tuple, count in group_tree_counts.items():
            obj = _create_group_obj(cls, group_param_tuple, count)
            create_groups.append(obj)
        cls.objects.bulk_create(create_groups)
        count = len(create_groups)
        num_create_groups += count
        log = f"Created {count} {cls.__name__}s."
        if count:
            LOG.info(log)
        else:
            LOG.verbose(log)  # type: ignore

    return num_create_groups > 0


def bulk_folders_modified(library, paths):
    """Update folders stat and nothing else."""
    if not paths:
        return False
    LOG.verbose(f"Preparing {len(paths)} folders for modification...")  # type: ignore
    folders = Folder.objects.filter(library=library, path__in=paths).only(
        "stat", "updated_at"
    )
    update_folders = []
    now = Now()
    for folder in folders:
        if Path(folder.path).exists():
            folder.set_stat()
            folder.updated_at = now  # type: ignore
            update_folders.append(folder)
    Folder.objects.bulk_update(
        update_folders, fields=BULK_UPDATE_FOLDER_MODIFIED_FIELDS
    )
    count = len(update_folders)
    log = f"Modified {count} folders"
    if count:
        LOG.info(log)
    else:
        LOG.verbose(log)  # type: ignore

    return count > 0


def bulk_create_folders(library, folder_paths):
    """Create folders breadth first."""
    if not folder_paths:
        return False

    LOG.verbose(f"Preparing {len(folder_paths)} folders for creation.")  # type: ignore
    # group folder paths by depth
    folder_path_dict = {}
    for path_str in folder_paths:
        path = Path(path_str)
        path_length = len(path.parts)
        if path_length not in folder_path_dict:
            folder_path_dict[path_length] = []
        folder_path_dict[path_length].append(path)

    # create each depth level first to ensure we can assign parents
    total_count = 0
    for _, paths in sorted(folder_path_dict.items()):
        create_folders = []
        for path in paths:
            name = path.name
            parent_path = str(Path(path).parent)
            if parent_path == library.path:
                parent = None
            else:
                parent = Folder.objects.get(path=parent_path)
            folder = Folder(
                library=library,
                path=str(path),
                name=name,
                parent_folder=parent,
            )
            folder.presave()
            folder.set_stat()
            create_folders.append(folder)
        Folder.objects.bulk_create(create_folders)
        count = len(create_folders)
        log = f"Created {count} Folders."
        if count:
            LOG.info(log)
        else:
            LOG.verbose(log)  # type: ignore
        if count:
            total_count += count
    return total_count > 0


def _bulk_create_named_models(cls, names):
    """Bulk create named models."""
    if not names:
        return False
    count = len(names)
    LOG.verbose(f"Preparing {count} {cls.__name__}s for creation...")  # type: ignore
    create_named_objs = []
    for name in names:
        named_obj = cls(name=name)
        create_named_objs.append(named_obj)

    cls.objects.bulk_create(create_named_objs)
    log = f"Created {count} {cls.__name__}s."
    if count:
        LOG.info(log)
    else:
        LOG.verbose(log)  # type: ignore
    return count > 0


def _bulk_create_credits(create_credit_tuples):
    """Bulk create credits."""
    if not create_credit_tuples:
        return False

    LOG.verbose(  # type: ignore
        f"Preparing {len(create_credit_tuples)} credits for creation..."
    )
    create_credits = []
    for role_name, person_name in create_credit_tuples:
        if role_name:
            role = CreditRole.objects.get(name=role_name)
        else:
            role = None
        person = CreditPerson.objects.get(name=person_name)
        credit = Credit(role=role, person=person)

        create_credits.append(credit)

    Credit.objects.bulk_create(create_credits)
    count = len(create_credits)
    log = f"Created {count} Credits."
    if count:
        LOG.info(log)
    else:
        LOG.verbose(log)  # type: ignore

    return count > 0


def bulk_create_all_fks(
    library, create_fks, create_groups, create_paths, create_credits
) -> bool:
    """Bulk create all foreign keys."""
    LOG.verbose(f"Creating comic foreign keys for {library.path}...")  # type: ignore
    changed = _bulk_create_groups(create_groups)
    changed |= bulk_create_folders(library, create_paths)
    for cls, names in create_fks.items():
        changed |= _bulk_create_named_models(cls, names)
    # This must happen after credit_fks created by create_named_models
    changed |= _bulk_create_credits(create_credits)
    return changed
