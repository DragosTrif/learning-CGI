#!/usr/bin/perl

use warnings;
use strict;

use CGI;
use CGI::Carp qw(fatalsToBrowser);
use DBI;

my $query = CGI->new();

my $database = 'my_store';
my $db_server = 'localhost';
my $user = 'user';
my $password = 'pass';

my ($session_id, $page_title, $cart_query, $dbh, $sth, $name, $address,
	$city, $state, $zip, $cc_type, $cc_number, $exp_month, $exp_year);
my %cc_types = ('AMEX' => 'American Express',
					'VISA' => 'Visa',
					'MC' => 'Mastercard',
					'DISC' => 'Discover',);

if ($query->cookie('session_id')) {
	$session_id = $query->cookie('session_id');
} else {
	$page_title = "Checkout: Error";
	print_page_start();
	print_no_cart();
	print_page_end();
	exit;
}

db_connect();
get_cart_contents();

if ($cart_query->rows) {
	if ($query->param('cc_type')) {
		set_variables();
		my $error_message = valid_form();
		if (!$error_message) {
			$page_title = "Checkout Complete";
			print_page_start();
			insert_order();
			empty_cart();
			print_success();
			print_page_end();
		} else {
			$page_title = "Checkout: Please correct errors";
			print_page_start();
			print_error($error_message);
			print_form();
			print_page_end();
		}
	} else {
		$page_title = "Checkout";
		print_page_start();
		print_form();
		print_page_end();
	}
} else {
	$page_title = "Error: Your cart is empty";
	print_page_start();
	print_no_cart();
	print_page_end();
}

db_cleanup();

sub print_page_start {
	print $query->header;
	print "<html>\n<head>\n<title>$page_title</title>\n";
	print "</head>\n<body>\n";
	print "<h1 align=\"center\">$page_title</h1>\n";
}

sub print_no_cart {
	print "<p>There are no items in your shopping cart.</p>\n";
}

sub print_page_end {
	print "<div align=\"center\"><b>";
	print"<a href=\"new_catalog.cgi\">return to catalog</a></b></div>\n";
	print "</body>\n</html>\n";
}

sub db_connect {
	$dbh = DBI->connect("DBI:mysql:$database:$db_server", $user,
	$password);
}

sub get_cart_contents {
	my $sql_select = qq[SELECT product_id, quantity
		FROM cart WHERE session_id = '$session_id'];
	$cart_query = $dbh->prepare($sql_select) or die "Couldn't prepare the query:", $cart_query->errstr, "\n";
	my $rv = $cart_query->execute or die "Couldn't execute select statement: ", $cart_query->errstr, "\n";	
}

sub print_form {
	print "<form>\n";
	print "<table border=\"0\">\n";
	print "<tr><td>Name:</td>\n";
	print "<td><input type=\"text\" name=\"name\" value=\"$name\" />\n";
	print "</td></tr>\n";
	print "<tr><td>Street address:</td>\n";
	print "<td><input type=\"text\" name=\"address\" ";
	print "value=\"$address\" size=\"40\" maxlength=\"80\" />";
	print "</td></tr>\n";
	print "<tr><td>City:</td>\n";
	print "<td><input type=\"text\" name=\"city\" ";
	print "value=\"$city\" /></td></tr>\n";
	print "<tr><td>State:</td>\n";
	print "<td><input type=\"text\" name=\"state\" ";
	print "value=\"$state\" size=\"2\" maxlength=\"2\" /></td></tr>\n";
	print "<tr><td>Zip</td>\n";
	print "<td><input type=\"text\" name=\"zip\" ";
	print "value=\"$zip\" size=\"5\" maxlength=\"5\"></td></tr>\n";
	print "<td>Credit card:</td>\n<td>\n<select name=\"cc_type\">\n";
	foreach my $key (sort {$a <=> $b} keys %cc_types) {
		print "<option value=\"$key\">", $cc_types{$key}, "\n";
	}
	print "</select>\n</td>\n";
	print "<tr><td>Credit card number:</td>\n";
	print "<td><input type=\"text\" name=\"cc_number\" ";
	print "value=\"$cc_number\" /></td></tr>\n";
	print "<tr><td>Expiration date:</td>\n";
	print "<td><input type=\"text\" name=\"exp_month\" ";
	print "value=\"$exp_month\" size=\"2\" maxlength=\"2\" />\n";
	print "<input type=\"text\" name=\"exp_year\" ";
	print "value=\"$exp_year\" size=\"4\" maxlength=\"4\" />\n";
	print "<tr><td></td>\n";
	print "<td><input type=\"submit\" value=\"Complete Checkout\" />";
	print "</td></tr>\n";
	print "</table>\n";
	print "</form>\n";
}

sub set_variables {
	$name = $query->param('name');
	$address = $query->param('address');
	$city = $query->param('city');
	$state = $query->param('state');
	$zip = $query->param('zip');
	$cc_type = $query->param('cc_type');
	$cc_number = $query->param('cc_number');
	$exp_month = $query->param('exp_month');
	$exp_year = $query->param('exp_year');
}

sub valid_form {
	my $error_message = '';
	$error_message .="<li>You must enter your name</li>\n" if ($name =~ /^\s*$/);
	$error_message .="<li>You must enter your address</li>\n" if ($address =~ /^\s*$/);
	$error_message .="<li>You must enter your city</li>\n" if ($city =~ /^\s*$/);
	$error_message .="<li>You must enter a valid zip code</li>\n" if ($zip !~ /^\d+$/);

	if ($exp_month > 12 || $exp_month < 1) {
		$error_message .="<li>You must enter a valid";
		$error_message .="expiration month.</li>\n";
	}	
	if ($exp_year < 2000 || $exp_year > 2010) {
		$error_message .="<li>You must enter a valid expiration";
		$error_message .="year</li>\n"
	}
	if ($cc_number !~ /^\d+$/) {
		$error_message .="<li>You must enter a valid credit card";
		$error_message .="number</li>\n"
	}
	return $error_message;
}

sub print_error {
	my $error_message = shift;
	print"<p>Please correct the following errors:</p>\n";
	if ($error_message) {
		print"<ul>\n$error_message\n</ul>\n";
	}
}

sub insert_order {
	# Create a unique Order ID
	my $order_id = time . $$;
	# Insert all of the items in the user's cart into the
	# order_products table
	while (my @row = $cart_query->fetchrow_array) {
		my ($product_id, $quantity) = @row;
		my $sql_insert_order_products = qq[INSERT INTO order_products (order_id, product_id, quantity)
			VALUES(?, ?, ?)];

		$sth = $dbh->prepare($sql_insert_order_products) or die"Couldn't prepare the query:", $sth->errstr,"\n";
		my $rv = $sth->execute($order_id, $product_id, $quantity) or die"Couldn't execute insert statement:", $sth->errstr,"\n";

	}
	# Create a record for the order itself
	my $place_holder = "?," x 9;
	my $sql_insert_orders = qq[ INSERT INTO orders (order_id, name, addr, city, state, zip, cc_number, cc_type, cc_exp_month, cc_exp_year)
		VALUES($place_holder ?) ];

	my $sth = $dbh->prepare($sql_insert_orders) or die"Couldn't prepare the query:", $sth->errstr,"\n";

	my $rv = $sth->execute($order_id, $name, $address,$city, $state, 
		$zip, $cc_number, $cc_type, $exp_month, $exp_year) or die"Order insert failed:", $sth->errstr,"\n";	
}

sub empty_cart {
	my $sql_delete = qq[DELETE FROM cart
		WHERE session_id = $session_id];

	$sth = $dbh->prepare($sql_delete)or die "Couldn't prepare the query:", $sth->errstr, "\n";
	my $rv = $sth->execute or die "Couldn't execute delete statement: ", $sth->errstr, "\n";
	
}

sub print_success {
	print "<p>Your order is complete.</p>\n";
}

sub db_cleanup {
	my $rc;
	if ($sth) {
		$rc = $sth->finish;
	}
	if ($cart_query) {
		$rc = $cart_query->finish;
	}
	$rc = $dbh->disconnect;
}
