#![warn(clippy::all)]

use clap::{App, AppSettings, Arg, ArgMatches};
use std::error::Error;

//mod panic_handler;
mod version;
mod windows_dialog;

fn handle_open_command(matches: &ArgMatches) -> Result<(), Box<dyn Error>> {
	// Expect filters to be given as description1, filter1, description2, filter2
	let filters: Vec<(&str, &str)> = match matches.values_of("filters") {
		Some(filter_args) if filter_args.len() > 0 => filter_args
			.collect::<Vec<&str>>()
			.chunks_exact(2)
			.map(|chunk| (chunk[0], chunk[1]))
			.collect(),
		// If a zero length filter is supplied then the dialog will have no file ext dropdown
		// Supplying a default filter ensures a file ext dropdown is shown.
		_ => vec![("All Files", "*.*")],
	};

	match windows_dialog::dialog_open(filters) {
		Ok(path) => {
			print!("{}", path);
			Ok(())
		}
		Err(error) if error.is::<windows_dialog::UserCancelled>() => Ok(()),
		Err(error) => Err(error),
	}
}

fn main() -> Result<(), Box<dyn Error>> {
	let matches = App::new("07th-mod Installer Loader")
		.setting(AppSettings::SubcommandRequiredElseHelp)
		.version(version::travis_tag())
		.about("Loader which extracts and starts the Python-based 07th-mod Installer.")
		.subcommand(
			App::new("open")
				.about(
					r#"Shows an open dialog and:
- if user selected a path, writes the chosen path to stdout, returns 0
- if user cancelled, writes nothing to stdout, returns 0
- if an error occurred, writes the error to stdout, returns 1"#,
				)
				.arg(
					Arg::with_name("filters")
						.help(
							r#"Sets the description and filters to use - defaults to all files.
For example, open "text and pdf" "*.txt;*.pdf" "main c file" "main.c""#,
						)
						.multiple(true),
				),
		)
		.get_matches();

	if let Some(matches) = matches.subcommand_matches("open") {
		return handle_open_command(matches);
	}

	Ok(())
}
